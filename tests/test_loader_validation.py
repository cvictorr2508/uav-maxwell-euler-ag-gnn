import json
import shutil
import tempfile
import unittest
from pathlib import Path

from uav_euler2d.loader import Euler2DDataset
from uav_euler2d.validation import ValidationConfig, integrate_surface, validate_dataset


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


if __name__ == "__main__":
    unittest.main()
