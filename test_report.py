import unittest
import HtmlTestRunner

# Define your test cases
from tests.unit_tests.models.test_queue_message_content import TestUpload, TestUploadData, TestToJson, TestValidationResult
from tests.unit_tests.test_validation import TestOtherValidation, TestValidation
from tests.unit_tests.test_osw_validator import TestOSWValidator
from tests.unit_tests.test_main import TestApp

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    # Add your test cases to the test suite
    test_suite.addTest(unittest.makeSuite(TestUpload))
    test_suite.addTest(unittest.makeSuite(TestUploadData))
    test_suite.addTest(unittest.makeSuite(TestToJson))
    test_suite.addTest(unittest.makeSuite(TestValidationResult))
    test_suite.addTest(unittest.makeSuite(TestOtherValidation))
    test_suite.addTest(unittest.makeSuite(TestValidation))
    test_suite.addTest(unittest.makeSuite(TestOSWValidator))
    test_suite.addTest(unittest.makeSuite(TestApp))

    # Define the output file for the HTML report
    output_file = 'test_report.html'

    # Open the output file in write mode
    with open(output_file, 'w') as f:
        # Create an HTMLTestRunner instance with the output file and customize the template
        runner = HtmlTestRunner.HTMLTestRunner(stream=f, report_title='OSW Test Report', combine_reports=True)

        # Run the test suite with the HTMLTestRunner
        runner.run(test_suite)

    print(f'\nRunning the tests complete.. see the report at {output_file}')
