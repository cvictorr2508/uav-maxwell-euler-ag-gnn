import json
import shutil
import tempfile
import unittest
from pathlib import Path

from uav_euler2d.loader import Euler2DDataset
from uav_euler2d.graph import build_surface_graph
from uav_euler2d.validation import ValidationConfig, integrate_surface, validate_dataset


class SyntheticDataset:
    """Small in-memory dataset used to exercise the complete validator."""

    root = Path("synthetic-root")
    split_manifest = {
        "train": ["g0"],
        "val": ["g1"],
        "test": ["g2"],
        "excluded_failed": ["g3"],
    }

    def __init__(self, bad_length=False):
        self._rows = {
            "c0": self._surface_rows("c0", bad_length),
            "c1": self._surface_rows("c1", False),
            "c2": self._surface_rows("c2", False),
            "c3": self._surface_rows("c3", False),
        }
        self._cases = (
            self._case("c0", "g0", "success"),
            self._case("c1", "g0", "non_converged"),
            self._case("c2", "g1", "success"),
            self._case("c3", "g2", "success"),
            self._case("c4", "g3", "failed"),
        )

    @staticmethod
    def _surface_rows(case_id, bad_length):
        cps = (0.5, 0.2, 0.0, 0.0)
        normals = ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0))
        rows = []
        for index, (cp, (nx, ny)) in enumerate(zip(cps, normals)):
            rows.append({
                "case_id": case_id,
                "entity_id": f"face-{index}",
                "contour_index": index,
                "x_m": float(index),
                "y_m": 0.0,
                "normal_x": nx,
                "normal_y": ny,
                "segment_length_m": 0.0 if bad_length and index == 0 else 1.0,
                "pressure_abs_Pa": 100.0 + cp * 10.0,
                "Cp": cp,
            })
        return tuple(rows)

    @staticmethod
    def _case(case_id, geometry_id, status):
        if status == "failed":
            return {"case_id": case_id, "geometry_id": geometry_id, "status": status,
                    "CL": "", "CD": "", "alpha_deg": "2", "chord_ref_m": "1",
                    "surface_file": ""}
        return {
            "case_id": case_id, "geometry_id": geometry_id, "status": status,
            "CL": "-0.2", "CD": "-0.5", "CL_final": "-0.2", "CD_final": "-0.5",
            "alpha_deg": "0", "chord_ref_m": "1", "rho_inf_kg_m3": "1",
            "p_inf_Pa": "100", "T_inf_K": "300", "gamma": "1.4",
            "V_inf_m_s": "10", "q_inf_Pa": "10",
            "surface_file": f"surface/case_{case_id}.parquet",
        }

    @property
    def cases(self):
        return self._cases

    def physical_constants(self):
        return {"p_inf_Pa": 100.0, "q_inf_Pa": 10.0, "rho_inf_kg_m3": 1.0,
                "V_inf_m_s": 10.0, "chord_ref_m": 1.0, "gamma": 1.4}

    def surface_rows(self, case_id):
        return self._rows[case_id]

    def case(self, case_id):
        return next(row for row in self._cases if row["case_id"] == case_id)

    def surface_path(self, case_id):
        return self.root / self.case(case_id)["surface_file"]


class LoaderPolicyTests(unittest.TestCase):
    def test_filter_policy_counts_from_fixture(self):
        root = Path(tempfile.mkdtemp(prefix="fixture-", dir=Path.cwd()))
        try:
            (root / "surface").mkdir()
            (root / "cases.csv").write_text(
                "case_id,geometry_id,status,CL,CD,alpha_deg,chord_ref_m,surface_file\n"
                "c0,g0,success,0.5,0.1,2,1,surface/case_c0.parquet\n"
                "c1,g1,non_converged,0.5,0.1,2,1,surface/case_c1.parquet\n"
                "c2,g2,failed,,,2,1,\n", encoding="utf-8"
            )
            (root / "dataset_manifest.json").write_text(json.dumps({"conditions": {"p_inf_Pa": 1, "q_inf_Pa": 1, "rho_inf_kg_m3": 1, "V_inf_m_s": 1, "chord_ref_m": 1}}), encoding="utf-8")
            (root / "split_manifest.json").write_text(json.dumps({"train": ["g0"], "val": ["g1"], "test": [], "excluded_failed": ["g2"]}), encoding="utf-8")
            (root / "meshes").mkdir()
            (root / "meshes/mesh_metadata.json").write_text("{}", encoding="utf-8")
            dataset = Euler2DDataset(root)
            self.assertEqual(len(dataset.cases_for_split("train", ("success",))), 1)
            self.assertEqual(len(dataset.cases_for_split("val", ("success",))), 0)
            self.assertEqual(len(tuple(dataset.iter_cases(("success", "non_converged")))), 2)
        finally:
            shutil.rmtree(root)

    def test_force_projection_uses_external_body_normal(self):
        rows = [
            {"Cp": 1.0, "normal_x": 0.0, "normal_y": 1.0, "segment_length_m": 1.0},
            {"Cp": 0.0, "normal_x": 0.0, "normal_y": -1.0, "segment_length_m": 1.0},
        ]
        cl, cd = integrate_surface(rows, alpha_deg=0.0, chord=1.0)
        self.assertAlmostEqual(cl, -1.0)
        self.assertAlmostEqual(cd, 0.0)

    def test_validate_dataset_covers_physics_partitions_and_repeated_geometry(self):
        report = validate_dataset(SyntheticDataset())
        self.assertTrue(report.passed, report.errors)
        self.assertEqual(report.metrics["success_by_split"], {"train": 1, "val": 1, "test": 1})
        self.assertEqual(report.metrics["case_count"], 5)

    def test_validate_dataset_rejects_nonpositive_segment_length(self):
        report = validate_dataset(SyntheticDataset(bad_length=True))
        self.assertFalse(report.passed)
        self.assertTrue(any("segment_length_m must be positive" in error for error in report.errors))

    def test_surface_graph_preserves_contour_only_and_provenance(self):
        graph = build_surface_graph(SyntheticDataset(), "c0")
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.contour_edges), 4)
        self.assertEqual(graph.volumetric_edges, ())
        self.assertEqual(graph.source_parquet, "surface/case_c0.parquet")
        self.assertEqual(graph.contour_edges[-1].target, graph.nodes[0].node_id)
        self.assertEqual(graph.nodes[0].attributes["Cp"], 0.5)


if __name__ == "__main__":
    unittest.main()
