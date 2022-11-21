from __future__ import annotations


class TestCase:
    def __init__(self, name: str) -> None:
        self.name = name

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def run(self, result: TestResult):
        result.test_started()
        self.set_up()
        try:
            method = getattr(self, self.name)
            method()
        except Exception:
            result.test_failed()
        self.tear_down()


class WasRun(TestCase):
    def set_up(self):
        self.was_set_up = 1
        self.log = "set_up "

    def test_method(self):
        self.log = self.log + "test_method "

    def test_broken_method(self):
        raise Exception

    def tear_down(self):
        self.log = self.log + "tear_down "


class TestResult:
    def __init__(self) -> None:
        self.run_count = 0
        self.error_count = 0

    def test_started(self):
        self.run_count += 1

    def test_failed(self):
        self.error_count += 1

    def summary(self) -> str:
        return "%d run, %d failed" % (self.run_count, self.error_count)


class TestSuite:
    def __init__(self) -> None:
        self.tests = list()

    def add(self, test: TestCase):
        self.tests.append(test)

    def run(self, result: TestResult):
        for test in self.tests:
            test.run(result)


class TestCaseTest(TestCase):
    def set_up(self):
        self.result = TestResult()

    def test_template_method(self):
        test = WasRun("test_method")
        test.run(self.result)
        assert "set_up test_method tear_down " == test.log

    def test_result(self):
        test = WasRun("test_method")
        test.run(self.result)
        assert "1 run, 0 failed" == self.result.summary()

    def test_failed_result(self):
        test = WasRun("test_broken_method")
        test.run(self.result)
        assert "1 run, 1 failed" == self.result.summary()

    def test_failed_result_formatting(self):
        self.result.test_started()
        self.result.test_failed()
        assert "1 run, 1 failed" == self.result.summary()

    def test_suite(self):
        suite = TestSuite()
        suite.add(WasRun("test_method"))
        suite.add(WasRun("test_broken_method"))
        suite.run(self.result)
        assert "2 run, 1 failed" == self.result.summary()


suite = TestSuite()
suite.add(TestCaseTest("test_template_method"))
suite.add(TestCaseTest("test_result"))
suite.add(TestCaseTest("test_failed_result"))
suite.add(TestCaseTest("test_failed_result_formatting"))
suite.add(TestCaseTest("test_suite"))
result = TestResult()
suite.run(result)
print(result.summary())
