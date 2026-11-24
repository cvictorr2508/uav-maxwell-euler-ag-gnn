"""Regression tests for preparation and inference contracts; no fitting occurs."""
from dataclasses import asdict, replace
import contextlib
import copy
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from test_loader_validation import SyntheticDataset
from uav_euler2d.execution import (
    DatasetValidationError, Standardizer, SurfacePreprocessor, prepare_experiment,
    require_valid_dataset, reserve_output, write_json,
    validate_flow_conditions,
)
from uav_euler2d.graph import SurfaceGraph, SurfaceNode, _make_edge, validate_contour
from uav_euler2d.validation import integrate_surface
from uav_euler2d.validation import validate_dataset
from uav_euler2d import kriging, rede_grafos_v4_freada as v4

NUMPY = importlib.util.find_spec("numpy") is not None
TORCH_STACK = NUMPY and all(importlib.util.find_spec(m) is not None for m in ("torch", "torch_geometric"))


def square(labelled=True):
    q = math.sqrt(.5)
    coords = ((0.,0.),(1.,0.),(1.,1.),(0.,1.))
    normals = ((-q,-q),(q,-q),(q,q),(-q,q))
    nodes = tuple(SurfaceNode(str(i), "c", "g", str(i), i, x, y, *normals[i], 1., {},
                  {"x_over_c":x,"y_over_c":y,"s_over_c":i/4.,"side":"upper" if i>1 else "lower"},
                  {"Cp":float(i)} if labelled else {}) for i,(x,y) in enumerate(coords))
    forward = tuple(_make_edge(nodes[i],nodes[(i+1)%4],"forward","boundary_contour") for i in range(4))
    reverse = tuple(_make_edge(nodes[(i+1)%4],nodes[i],"reverse","boundary_contour_reverse") for i in range(4))
    return SurfaceGraph("c","g","synthetic",nodes,forward,reverse_edges=reverse,
                        graph_inputs={"mach_inf":.8,"alpha_deg":0.},graph_targets={"CL":1.,"CD":.1})


class RichDataset(SyntheticDataset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for row in self._cases:
            row.update(m="0.02",p="0.4",t="0.12",mach_inf="0.8")
        for rows in self._rows.values():
            for row in rows:
                row.update(x_over_c=row["x_m"], y_over_c=row["y_m"], s_over_c=row["contour_index"]/4., side="upper")


class ContourRegressionTests(unittest.TestCase):
    def test_both_traversals_preserve_external_normal_validity(self):
        nodes = square().nodes
        self.assertTrue(validate_contour(nodes,"c",strict=True)["passed"])
        self.assertTrue(validate_contour(tuple(reversed(nodes)),"c",strict=True)["passed"])
        inward = tuple(replace(n,normal_x=-n.normal_x,normal_y=-n.normal_y) for n in nodes)
        self.assertFalse(validate_contour(inward,"c")["passed"])

    def test_nonfinite_geometry_is_reported_not_accepted(self):
        for key in ("normal_x","x_m","segment_length_m"):
            nodes = (replace(square().nodes[0],**{key:math.nan}),) + square().nodes[1:]
            report = validate_contour(nodes,"c")
            self.assertFalse(report["passed"])
            json.dumps(report,allow_nan=False)
            with self.assertRaises(ValueError):
                validate_contour(nodes,"c",strict=True)

    def test_empty_contour_and_bad_reference_are_rejected(self):
        self.assertFalse(validate_contour((),"empty")["passed"])
        with self.assertRaises(ValueError):
            replace(square(),chord_ref_m=0.).to_arrays()

    @unittest.skipUnless(NUMPY,"array export requires optional NumPy")
    def test_inference_without_labels_and_no_target_leakage(self):
        graph = square(False)
        result = graph.to_arrays()
        self.assertIsNone(result["node_targets"])
        self.assertEqual(result["node_features"].shape,(4,7))
        self.assertEqual(result["edge_index"].shape,(2,8))
        labelled = square().to_arrays(require_targets=True)
        self.assertTrue((result["node_features"] == labelled["node_features"]).all())
        self.assertEqual(labelled["node_targets"].shape,(4,1))
        with self.assertRaises(ValueError):
            graph.to_arrays(require_targets=True)

    def test_every_node_and_partial_labels_are_validated(self):
        graph = square()
        for node in (replace(graph.nodes[-1],inputs={}),
                     replace(graph.nodes[-1],targets={}),
                     replace(graph.nodes[-1],inputs={**graph.nodes[-1].inputs,"x_over_c":math.nan})):
            with self.assertRaises(ValueError):
                replace(graph,nodes=graph.nodes[:-1]+(node,)).to_arrays()

    def test_integration_uses_case_angle_chord_and_accepts_generators(self):
        rows = [{"Cp":1.,"normal_x":0.,"normal_y":1.,"segment_length_m":1.}]
        cl,cd = integrate_surface(iter(rows),0.,2.)
        self.assertAlmostEqual(cl,-.5)
        self.assertAlmostEqual(cd,0.)
        cl,cd = integrate_surface(iter(rows),90.,2.)
        self.assertAlmostEqual(cl,0.)
        self.assertAlmostEqual(cd,-.5)


class PreparationRegressionTests(unittest.TestCase):
    def test_preparation_keeps_manifest_and_excludes_nonconverged(self):
        dataset = RichDataset()
        original = copy.deepcopy((dataset.cases,dataset.split_manifest))
        prepared = prepare_experiment(dataset)
        self.assertFalse(prepared["training_executed"])
        self.assertEqual(prepared["case_ids"],{"train":["c0"],"val":["c2"],"test":["c3"]})
        self.assertEqual(original,(dataset.cases,dataset.split_manifest))

    def test_validator_exceptions_fail_closed(self):
        dataset = RichDataset()
        dataset.physical_constants = lambda: {"p_inf_Pa":100.,"q_inf_Pa":0.,"rho_inf_kg_m3":1.,"V_inf_m_s":1.,"chord_ref_m":1.,"gamma":1.4}
        with self.assertRaises(DatasetValidationError):
            require_valid_dataset(dataset)

    def test_zero_coefficients_use_absolute_tolerance_without_division(self):
        dataset = RichDataset()
        for row in dataset.cases:
            if row["status"] != "failed":
                row.update(CL="0",CD="0",CL_final="0",CD_final="0")
        for rows in dataset._rows.values():
            for row in rows:
                row.update(Cp=0.,pressure_abs_Pa=100.)
        report = validate_dataset(dataset)
        self.assertTrue(report.passed,report.errors)
        self.assertIsNone(report.metrics["c0.CL_relative_pct"])
        json.dumps(report.metrics,allow_nan=False)

    def test_both_entrypoints_block_invalid_data_before_ml_or_outputs(self):
        import builtins
        original_import = builtins.__import__
        def guarded(name,*args,**kwargs):
            if name.split('.')[0] in {"torch","torch_geometric","sklearn","numpy","joblib"}:
                raise AssertionError("ML dependency touched before validation")
            return original_import(name,*args,**kwargs)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            for module in (kriging,v4):
                output = Path(tmp)/module.__name__.split('.')[-1]
                with mock.patch.object(module,"Euler2DDataset",return_value=RichDataset(bad_length=True)), mock.patch("builtins.__import__",side_effect=guarded), contextlib.redirect_stderr(io.StringIO()) as error:
                    result = module.main(["synthetic","--execute","--output",str(output)])
                self.assertEqual(result,2)
                self.assertFalse(json.loads(error.getvalue())["training_executed"])
                self.assertFalse(output.exists())

    def test_default_gpr_command_only_prepares(self):
        with mock.patch.object(kriging,"Euler2DDataset",return_value=RichDataset()), contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(kriging.main(["synthetic"]),0)
        self.assertEqual(json.loads(stdout.getvalue())["status"],"prepared")

    @unittest.skipUnless(NUMPY,"GNN preparation exports optional NumPy arrays")
    def test_default_gnn_command_uses_shared_graph_without_training(self):
        with mock.patch.object(v4,"Euler2DDataset",return_value=RichDataset()), mock.patch.object(v4,"build_surface_graph",wraps=v4.build_surface_graph) as builder, contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(v4.main(["synthetic"]),0)
        self.assertEqual([c.args[1] for c in builder.call_args_list],["c0","c2"])
        self.assertFalse(json.loads(stdout.getvalue())["training_executed"])

    def test_imports_are_side_effect_free_without_optional_libraries(self):
        src = str(Path(__file__).resolve().parents[1]/"src")
        code = """import builtins
original = builtins.__import__
def guard(name, *args, **kwargs):
    if name.split('.')[0] in {'torch','torch_geometric','sklearn','pandas','numpy','pyarrow'}:
        raise AssertionError(name)
    return original(name,*args,**kwargs)
builtins.__import__ = guard
import uav_euler2d.kriging
import uav_euler2d.rede_grafos_v4_freada
print('import-safe')
"""
        result = subprocess.run([sys.executable,"-B","-c",code],env={**os.environ,"PYTHONPATH":src},capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),"import-safe")

    def test_outputs_cannot_overwrite_dataset_or_existing_artifacts(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            dataset = Path(tmp)/"dataset"
            dataset.mkdir()
            with self.assertRaises(ValueError):
                reserve_output(dataset/"results",dataset)
            output = reserve_output(Path(tmp)/"run",dataset)
            with self.assertRaises(FileExistsError):
                reserve_output(output,dataset)
            write_json(output/"state.json",{"value":1})
            with self.assertRaises(FileExistsError):
                write_json(output/"state.json",{"value":2})


class PreprocessingRegressionTests(unittest.TestCase):
    def test_incomplete_or_nonfinite_saved_flow_fails_before_inference(self):
        invalid = (None, {}, {"mach_inf": .8},
                   {"mach_inf": math.nan, "alpha_deg": 2.},
                   {"mach_inf": .8, "alpha_deg": math.inf},
                   {"mach_inf": -1., "alpha_deg": 2.},
                   {"mach_inf": True, "alpha_deg": 2.},
                   {"mach_inf": .8, "alpha_deg": 2., "extra": 1.})
        for conditions in invalid:
            with self.subTest(conditions=conditions):
                with self.assertRaises(ValueError):
                    validate_flow_conditions(conditions)
                with self.assertRaises(ValueError):
                    v4.predict_cp(SimpleNamespace(flow_conditions=conditions), None, square(False))
        model = mock.Mock()
        artifact = {"schema_version": 1, "features": ["m", "p", "t"],
                    "flow_conditions": {}, "model": model}
        with self.assertRaises(ValueError):
            kriging.predict_cl(artifact, [{"mach_inf": .8, "alpha_deg": 0.}])
        model.predict.assert_not_called()

    def test_train_statistics_are_stable_after_heldout_transformation(self):
        scale = Standardizer.fit([[1.,0.],[3.,1.]],preserve=(1,))
        saved = scale.to_dict()
        self.assertEqual(scale.mean,(2.,0.))
        self.assertEqual(scale.transform([[2.,1.]]),[[0.,1.]])
        self.assertGreater(scale.transform([[100.,0.]])[0][0],60.)
        self.assertEqual(saved,scale.to_dict())
        self.assertEqual(Standardizer.from_dict(json.loads(json.dumps(saved))),scale)

    def test_bad_and_constant_training_values(self):
        for rows in ([],[[1.],[1.,2.]],[[math.nan]]):
            with self.assertRaises(ValueError):
                Standardizer.fit(rows)
        self.assertEqual(Standardizer.fit([[2.],[2.]]).transform([[2.]]),[[0.]])
        with self.assertRaises(ValueError):
            Standardizer.from_dict({"mean":[1.],"scale":[0.]})

    def test_complete_surface_preprocessing_roundtrip(self):
        data = {"schema_version":1,"nodes":Standardizer.fit([[0.]*7,[1.]*7],preserve=(6,)).to_dict(),
                "edges":Standardizer.fit([[0.]*5,[1.]*5]).to_dict(),"cp":Standardizer.fit([[0.],[1.]]).to_dict()}
        restored = SurfacePreprocessor.from_dict(json.loads(json.dumps(data)))
        self.assertEqual(restored.to_dict(),data)
        del data["edges"]
        with self.assertRaises(KeyError):
            SurfacePreprocessor.from_dict(data)

    def test_gpr_inference_reuses_saved_input_scaling(self):
        model = mock.Mock()
        model.predict.return_value = ([1.],[.2])
        row = {"m":.02,"p":.4,"t":.12,"mach_inf":.8,"alpha_deg":2.}
        artifact = {"schema_version":1,"features":["m","p","t"],"lower":kriging.LOWER,"upper":kriging.UPPER,
                    "model":model,"flow_conditions":{"mach_inf":.8,"alpha_deg":2.}}
        self.assertEqual(kriging.predict_cl(artifact,[row]),([1.],[.2]))
        for value in model.predict.call_args.args[0][0]:
            self.assertAlmostEqual(value,.5)
        with self.assertRaises(ValueError):
            kriging.predict_cl(artifact,[{**row,"alpha_deg":3.}])

    def test_config_and_zero_mean_metric_are_explicit(self):
        with self.assertRaises(ValueError):
            v4.NetworkConfig(epochs=0).validate()
        result = v4.metricas([1.,-1.],[0.,0.],[0.,0.],[0.,0.])
        self.assertIsNone(result["CL_percent_of_mean"])
        self.assertAlmostEqual(result["CL"],1.)

    @unittest.skipUnless(TORCH_STACK,"optional PyTorch/PyG stack unavailable; no installation or training")
    def test_untrained_checkpoint_roundtrip_and_unlabelled_forward(self):
        import torch
        graph = square()
        data = v4.graph_to_data(graph,require_targets=True)
        prep = SurfacePreprocessor.fit([data])
        config = v4.NetworkConfig()
        model = v4.RedeGrafos(config)
        model.flow_conditions = graph.graph_inputs
        self.assertEqual(sum(p.numel() for p in model.parameters()),41857)
        no_labels = replace(graph,nodes=tuple(replace(n,targets={}) for n in graph.nodes),graph_targets={})
        before = v4.predict_cp(model,prep,no_labels)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp)/"untrained.pt"
            torch.save({"schema_version":1,"state_dict":model.state_dict(),"configuration":asdict(config),
                        "preprocessing":prep.to_dict(),"node_features":list(v4.NODE_FEATURE_NAMES),
                        "edge_features":list(v4.V4_EDGE_FEATURES),"flow_conditions":graph.graph_inputs},path)
            loaded,restored,_ = v4.load_checkpoint(path)
            self.assertTrue(torch.allclose(before,v4.predict_cp(loaded,restored,no_labels)))


if __name__ == "__main__":
    unittest.main()
