"""Offline checks: all Smartsheet calls are mocked."""
import csv
import contextlib
from datetime import date
import io
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from deap import base

from parameters import Parameters
from smartsheet_handler import SmartsheetHandler
from task_assignment import TaskAssignment


class ConfigurationSafety(unittest.TestCase):
    def parameters(self, **overrides):
        values = {
            "SELECTED_PROJECT": "project4",
            "SMARTSHEET_API_KEY": "test-api-key",
            "PROJECT4_PROJECTS_TASKS_SHEET_ID": "101",
            "PROJECT4_MEMBERS_SHEET_ID": "102",
        }
        with patch.dict(os.environ, dict(values, **overrides), clear=True), \
                patch("parameters.load_dotenv"):
            return Parameters()

    def test_read_only_mode_does_not_require_export_destinations(self):
        self.parameters().validate_smartsheet_config()

    def test_write_mode_requires_explicit_destinations(self):
        with self.assertRaisesRegex(ValueError, "RESOURCE_OPTIMIZER_SHEET_ID"):
            self.parameters().validate_smartsheet_config(allow_writes=True)

    def test_placeholder_key_and_non_numeric_sheet_are_rejected(self):
        for values in ({"SMARTSHEET_API_KEY": "your_api_key_here"},
                       {"PROJECT4_MEMBERS_SHEET_ID": "not-a-sheet"}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.parameters(**values).validate_smartsheet_config()

    def test_unknown_project_has_a_clear_error(self):
        with self.assertRaisesRegex(ValueError, "SELECTED_PROJECT"):
            self.parameters(SELECTED_PROJECT="unknown")


class SmartsheetWriteSafety(unittest.TestCase):
    TITLES = ["Solution", "Population Size", "Num Generations", "Crossover Prob",
              "Crossover Type", "Mutation Prob", "Indpb", "Mutation Type",
              "Selection Type", "Objective Weights", "Constraint Weights",
              "Constraint Violations", "Project ID", "Project Name", "Task ID",
              "Task Name", "Start Date", "End Date", "Duration", "Budget",
              "Required Skills", "Prerequisite Tasks", "Member ID", "Member Name",
              "Member Skills", "Member Cost", "Actual Cost"]

    def handler(self):
        with patch("smartsheet_handler.smartsheet.Smartsheet") as factory:
            handler = SmartsheetHandler("test-api-key")
        return handler, factory.return_value.Sheets

    def test_default_handler_rejects_copy_and_write_before_network_io(self):
        handler, sheets = self.handler()
        with self.assertRaises(PermissionError):
            handler.copy_and_rename_sheet("101", "experiment", "201")
        with self.assertRaises(PermissionError):
            handler.write_data_to_sheet("101", [])
        sheets.get_sheet.assert_not_called()
        sheets.copy_sheet.assert_not_called()
        sheets.delete_rows.assert_not_called()
        sheets.add_rows.assert_not_called()

    def test_empty_output_cannot_clear_an_existing_sheet(self):
        handler, sheets = self.handler()
        handler.allow_writes = True
        sheets.get_sheet.return_value = SimpleNamespace(
            rows=[SimpleNamespace(id=1)],
            columns=[SimpleNamespace(title=title, id=index + 1)
                     for index, title in enumerate(self.TITLES)])
        with self.assertRaisesRegex(ValueError, "empty output"):
            handler.write_data_to_sheet("101", [])
        sheets.delete_rows.assert_not_called()
        sheets.add_rows.assert_not_called()

    def test_invalid_schema_is_rejected_before_deleting_existing_rows(self):
        handler, sheets = self.handler()
        handler.allow_writes = True
        sheets.get_sheet.return_value = SimpleNamespace(
            rows=[SimpleNamespace(id=1)], columns=[])
        with self.assertRaises(ValueError):
            handler.write_data_to_sheet("101", [Mock()])
        sheets.delete_rows.assert_not_called()
        sheets.add_rows.assert_not_called()

    def test_add_failure_preserves_existing_rows(self):
        handler, sheets = self.handler()
        handler.allow_writes = True
        sheets.get_sheet.return_value = SimpleNamespace(
            rows=[SimpleNamespace(id=1)],
            columns=[SimpleNamespace(title=title, id=index + 1)
                     for index, title in enumerate(self.TITLES)])
        task = SimpleNamespace(id=1, name="Task", start_date=date(2023, 1, 1),
                               end_date=date(2023, 1, 2), budget=100,
                               skill_set=["python"], prerequisite_tasks=[],
                               get_duration=lambda: 1)
        assignment = SimpleNamespace(task=task, assigned_member=None, solution=1,
                                     project_id=1, project_name="Project",
                                     constraint_violations=[],
                                     get_actual_cost=lambda: None,
                                     get_ga_parameters_values=lambda: [])
        sheets.add_rows.side_effect = RuntimeError("simulated write failure")
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            handler.write_data_to_sheet("101", [assignment])
        sheets.delete_rows.assert_not_called()

    def test_successful_replacement_adds_before_deleting_old_rows(self):
        handler, sheets = self.handler()
        handler.allow_writes = True
        sheets.get_sheet.return_value = SimpleNamespace(
            rows=[SimpleNamespace(id=1)],
            columns=[SimpleNamespace(title=title, id=index + 1)
                     for index, title in enumerate(self.TITLES)])
        task = SimpleNamespace(id=2, name="Task", start_date=date(2023, 1, 1),
                               end_date=date(2023, 1, 2), budget=100,
                               skill_set=["python"], prerequisite_tasks=[],
                               get_duration=lambda: 1)
        project = SimpleNamespace(id=1, name="Project")
        assignment = TaskAssignment(project, task, None, 1, [], [])
        handler.write_data_to_sheet("101", [assignment])
        self.assertEqual([call[0] for call in sheets.mock_calls],
                         ["get_sheet", "add_rows", "delete_rows"])
        sheets.delete_rows.assert_called_once_with("101", [1])


class CSVExportSafety(unittest.TestCase):
    def test_formula_like_names_are_exported_as_text(self):
        project = SimpleNamespace(id=1, name="=1+1")
        task = SimpleNamespace(id=2, name="\t=2+2", start_date=date(2023, 1, 1),
                               end_date=date(2023, 1, 2), budget=100,
                               skill_set=["python"], prerequisite_tasks=[])
        assignment = TaskAssignment(project, task, None, 1, [], [100, 1, 0.5])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assignments.csv"
            assignment.to_csv(str(path), "experiment")
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.reader(stream))
        self.assertIn("'=1+1", rows[1])
        self.assertIn("'\t=2+2", rows[1])
        self.assertEqual(rows[1][2:5], ["100", "1", "0.5"])

    def test_numeric_and_ordinary_values_are_unchanged(self):
        for value in (-5, 0.5, "Project", None):
            self.assertEqual(TaskAssignment._safe_csv_value(value), value)


class RunPolicy(unittest.TestCase):
    def run_experiment(self, allow_writes):
        import main

        params = ConfigurationSafety().parameters()
        first_name, first_set = next(iter(params.parameter_sets.items()))
        params.parameter_sets = {first_name: first_set}
        params.resource_optimizer_sheet_id = "301"
        params.folder_id = "401"
        task = SimpleNamespace(id=1, name="Task", start_date=date(2023, 1, 1),
                               end_date=date(2023, 1, 2), budget=100,
                               skill_set=["python"], prerequisite_tasks=[],
                               get_duration=lambda: 1)
        project = SimpleNamespace(id=1, name="Project", tasks=[task])
        member = SimpleNamespace(id=1, name="Member", skill_set=["python"], cost=50)

        class Individual(list):
            pass

        individual = Individual([0])
        individual.fitness = SimpleNamespace(values=(50, 0))
        individual.constraint_violations = [[]]
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(main, "__file__", str(Path(tmp) / "main.py")), \
                patch.object(main, "Parameters", return_value=params), \
                patch.object(main, "SmartsheetHandler") as factory, \
                patch.object(main.Optimizer, "optimize", return_value=[[individual]]), \
                patch.object(main, "ViolationWriter"), patch.object(main, "ParetoPlotter"), \
                contextlib.redirect_stdout(io.StringIO()):
            handler = factory.return_value
            handler.read_projects_tasks_from_sheet.return_value = [project]
            handler.read_members_from_sheet.return_value = [member]
            handler.copy_and_rename_sheet.return_value = SimpleNamespace(id=201)
            main.main(["--allow-smartsheet-writes"] if allow_writes else [])
            factory.assert_called_once_with("test-api-key", allow_writes=allow_writes)
            self.assertEqual(len(list((Path(tmp) / "results").rglob("task_assignments.csv"))), 1)
            if allow_writes:
                handler.copy_and_rename_sheet.assert_called_once_with("301", first_name, "401")
                self.assertEqual(handler.write_data_to_sheet.call_args[0][0], 201)
            else:
                handler.copy_and_rename_sheet.assert_not_called()
                handler.write_data_to_sheet.assert_not_called()

    def test_default_run_writes_local_csv_without_remote_exports(self):
        self.run_experiment(False)

    def test_explicit_write_flag_exports_only_to_the_copied_sheet(self):
        self.run_experiment(True)


class PlotCompatibility(unittest.TestCase):
    def test_synthetic_generations_produce_png_and_gif(self):
        from pareto_plotter import ParetoPlotter

        class Fitness(base.Fitness):
            weights = (-1.0, -1.0)

        generation = [
            SimpleNamespace(fitness=Fitness(values), original_objective_values=values,
                            constraint_violations=[[]])
            for values in ((100, 2), (200, 1))
        ]
        with tempfile.TemporaryDirectory() as tmp:
            plotter = ParetoPlotter(1, 2)
            plotter.plot_pareto_front_and_violations(tmp, [generation, generation], "test")
            plotter.plot_all_generations_pareto_front(tmp, [generation, generation], 1, "test", tmp)
            for name in ("pareto_front_and_violations_gen_001.png",
                         "pareto_front_all_generations.png"):
                self.assertTrue((Path(tmp) / name).read_bytes().startswith(b"\x89PNG"))
            for name in ("pareto_front_and_violations.gif",
                         "pareto_front_all_generations.gif"):
                self.assertTrue((Path(tmp) / name).read_bytes().startswith(b"GIF"))


if __name__ == "__main__":
    unittest.main()
