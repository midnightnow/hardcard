#!/usr/bin/env python3
"""
Medical validation script for VetSorcery workflow
Ensures medical test scenarios meet veterinary safety standards
"""

import json
import sys
import argparse
from typing import Dict, List, Any
from datetime import datetime

class MedicalValidator:
    def __init__(self):
        self.critical_thresholds = {
            'drug_calculation_accuracy': 100,
            'emergency_response_time': 500,  # ms
            'patient_data_integrity': 100,
            'dosage_safety_margin': 10  # percent
        }
        
        # Known drug interactions for validation
        self.known_interactions = {
            ('carprofen', 'prednisolone'): {'severity': 'major', 'description': 'Increased GI ulceration risk'},
            ('tramadol', 'selegiline'): {'severity': 'critical', 'description': 'Risk of serotonin syndrome'},
            ('metronidazole', 'warfarin'): {'severity': 'major', 'description': 'Enhanced anticoagulation'}
        }
    
    def validate_medical_impact(self, medical_impact: str, changed_files: List[str], commit_msg: str) -> Dict:
        """Validate medical impact assessment"""
        results = {
            'passed': True,
            'impact_level': medical_impact,
            'errors': [],
            'warnings': [],
            'requirements': []
        }
        
        # Check for medical-critical files
        medical_files = [f for f in changed_files if any(keyword in f.lower() 
                        for keyword in ['drug', 'patient', 'medical', 'emergency', 'dosage', 'pharmacy'])]
        
        if medical_files and medical_impact == 'low':
            results['passed'] = False
            results['errors'].append('Medical files changed but impact assessed as LOW')
            results['errors'].append(f'Medical files: {medical_files}')
        
        # High impact requirements
        if medical_impact == 'high':
            results['requirements'] = [
                'Manual review by veterinary staff required',
                '100% test coverage for affected functionality',
                'Drug interaction validation must pass',
                'Emergency protocol testing required',
                'Security scan must pass with 0 critical issues'
            ]
            
            # Check commit message format for high impact
            if 'MEDICAL-IMPACT: HIGH' not in commit_msg:
                results['warnings'].append('High impact commits should include "MEDICAL-IMPACT: HIGH" in message')
        
        return results
    
    def validate_drug_calculations(self, test_data: Dict) -> Dict:
        """Validate drug dosage calculations"""
        results = {
            'passed': True,
            'accuracy': 0,
            'errors': [],
            'total_tests': 0,
            'passed_tests': 0
        }
        
        calculations = test_data.get('dosage_calculations', [])
        results['total_tests'] = len(calculations)
        
        for calc in calculations:
            patient_weight = calc.get('patient_weight_kg', 0)
            drug_name = calc.get('drug_name', '')
            expected_dose = calc.get('expected_dose_mg', 0)
            calculated_dose = calc.get('calculated_dose_mg', 0)
            
            # Validate calculation accuracy (within 1% tolerance for rounding)
            if expected_dose > 0:
                accuracy = abs(calculated_dose - expected_dose) / expected_dose
                if accuracy <= 0.01:  # 1% tolerance
                    results['passed_tests'] += 1
                else:
                    results['errors'].append(
                        f"Dosage calculation error for {drug_name}: "
                        f"Expected {expected_dose}mg, got {calculated_dose}mg "
                        f"(error: {accuracy*100:.2f}%)"
                    )
            
            # Validate safety margins
            dose_per_kg = calculated_dose / patient_weight if patient_weight > 0 else 0
            
            # Common veterinary dosage safety checks
            safety_checks = {
                'tramadol': {'min': 2, 'max': 10, 'unit': 'mg/kg'},
                'carprofen': {'min': 2, 'max': 4, 'unit': 'mg/kg'},
                'meloxicam': {'min': 0.1, 'max': 0.2, 'unit': 'mg/kg'}
            }
            
            if drug_name.lower() in safety_checks:
                limits = safety_checks[drug_name.lower()]
                if dose_per_kg < limits['min'] or dose_per_kg > limits['max']:
                    results['errors'].append(
                        f"Unsafe dosage for {drug_name}: {dose_per_kg:.2f} {limits['unit']} "
                        f"(safe range: {limits['min']}-{limits['max']} {limits['unit']})"
                    )
                    results['passed'] = False
        
        if results['total_tests'] > 0:
            results['accuracy'] = (results['passed_tests'] / results['total_tests']) * 100
        
        if results['accuracy'] < self.critical_thresholds['drug_calculation_accuracy']:
            results['passed'] = False
            results['errors'].append(
                f"Drug calculation accuracy {results['accuracy']:.1f}% below required "
                f"{self.critical_thresholds['drug_calculation_accuracy']}%"
            )
        
        return results
    
    def validate_emergency_protocols(self, test_data: Dict) -> Dict:
        """Validate emergency response protocols"""
        results = {
            'passed': True,
            'response_times': [],
            'errors': [],
            'protocols_tested': 0
        }
        
        protocols = test_data.get('emergency_protocols', [])
        results['protocols_tested'] = len(protocols)
        
        for protocol in protocols:
            protocol_name = protocol.get('name', 'unknown')
            response_time = protocol.get('response_time_ms', float('inf'))
            required_steps = protocol.get('required_steps', [])
            executed_steps = protocol.get('executed_steps', [])
            
            results['response_times'].append(response_time)
            
            # Check response time
            if response_time > self.critical_thresholds['emergency_response_time']:
                results['passed'] = False
                results['errors'].append(
                    f"Emergency protocol '{protocol_name}' response time {response_time}ms "
                    f"exceeds limit {self.critical_thresholds['emergency_response_time']}ms"
                )
            
            # Check all required steps executed
            missing_steps = set(required_steps) - set(executed_steps)
            if missing_steps:
                results['passed'] = False
                results['errors'].append(
                    f"Emergency protocol '{protocol_name}' missing steps: {list(missing_steps)}"
                )
        
        return results
    
    def validate_patient_data_integrity(self, test_data: Dict) -> Dict:
        """Validate patient data handling"""
        results = {
            'passed': True,
            'errors': [],
            'data_validation_tests': 0,
            'integrity_score': 0
        }
        
        integrity_tests = test_data.get('patient_data_integrity', [])
        results['data_validation_tests'] = len(integrity_tests)
        passed_tests = 0
        
        for test in integrity_tests:
            test_name = test.get('test_name', 'unknown')
            expected_result = test.get('expected_result', '')
            actual_result = test.get('actual_result', '')
            
            if expected_result == actual_result:
                passed_tests += 1
            else:
                results['errors'].append(
                    f"Patient data integrity test '{test_name}' failed: "
                    f"expected '{expected_result}', got '{actual_result}'"
                )
        
        if results['data_validation_tests'] > 0:
            results['integrity_score'] = (passed_tests / results['data_validation_tests']) * 100
            
        if results['integrity_score'] < self.critical_thresholds['patient_data_integrity']:
            results['passed'] = False
            results['errors'].append(
                f"Patient data integrity score {results['integrity_score']:.1f}% "
                f"below required {self.critical_thresholds['patient_data_integrity']}%"
            )
        
        return results
    
    def generate_medical_report(self, medical_impact: str, test_data: Dict, 
                               changed_files: List[str], commit_msg: str) -> Dict:
        """Generate comprehensive medical validation report"""
        
        impact_validation = self.validate_medical_impact(medical_impact, changed_files, commit_msg)
        drug_validation = self.validate_drug_calculations(test_data)
        emergency_validation = self.validate_emergency_protocols(test_data)
        data_validation = self.validate_patient_data_integrity(test_data)
        
        overall_passed = all([
            impact_validation['passed'],
            drug_validation['passed'],
            emergency_validation['passed'],
            data_validation['passed']
        ])
        
        # Calculate overall medical safety score
        scores = []
        if drug_validation['accuracy'] > 0:
            scores.append(drug_validation['accuracy'])
        if data_validation['integrity_score'] > 0:
            scores.append(data_validation['integrity_score'])
        if emergency_validation['protocols_tested'] > 0:
            scores.append(100 if emergency_validation['passed'] else 0)
        
        safety_score = sum(scores) / len(scores) if scores else 0
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'medical_impact': medical_impact,
            'overall_status': 'PASS' if overall_passed else 'FAIL',
            'medical_safety_score': round(safety_score, 1),
            'validations': {
                'impact_assessment': impact_validation,
                'drug_calculations': drug_validation,
                'emergency_protocols': emergency_validation,
                'patient_data_integrity': data_validation
            },
            'summary': {
                'total_errors': sum(len(v.get('errors', [])) for v in [
                    impact_validation, drug_validation, emergency_validation, data_validation
                ]),
                'critical_requirements_met': overall_passed,
                'requires_manual_review': medical_impact == 'high'
            },
            'recommendations': self.generate_recommendations(
                impact_validation, drug_validation, emergency_validation, data_validation
            )
        }
        
        return report
    
    def generate_recommendations(self, impact_val: Dict, drug_val: Dict, 
                                emergency_val: Dict, data_val: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not impact_val['passed']:
            recommendations.append("Review medical impact assessment accuracy")
        
        if not drug_val['passed']:
            recommendations.append("Verify drug dosage calculation algorithms")
            recommendations.append("Review veterinary dosage guidelines")
        
        if not emergency_val['passed']:
            recommendations.append("Optimize emergency protocol response times")
            recommendations.append("Ensure all critical steps are included in protocols")
        
        if not data_val['passed']:
            recommendations.append("Strengthen patient data validation")
            recommendations.append("Review data integrity safeguards")
        
        if impact_val['impact_level'] == 'high':
            recommendations.append("Schedule manual review with veterinary staff")
            recommendations.append("Conduct additional safety testing before deployment")
        
        return recommendations

def main():
    parser = argparse.ArgumentParser(description='Validate medical safety aspects of VetSorcery changes')
    parser.add_argument('--medical-impact', required=True, choices=['low', 'medium', 'high'],
                       help='Medical impact level')
    parser.add_argument('--test-data', help='JSON file with test results')
    parser.add_argument('--changed-files', help='Comma-separated list of changed files')
    parser.add_argument('--commit-message', help='Commit message to analyze')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--output', help='Output file for detailed report')
    
    args = parser.parse_args()
    
    try:
        validator = MedicalValidator()
        
        # Load test data if provided
        test_data = {}
        if args.test_data:
            with open(args.test_data, 'r') as f:
                test_data = json.load(f)
        
        # Parse changed files
        changed_files = []
        if args.changed_files:
            changed_files = [f.strip() for f in args.changed_files.split(',')]
        
        commit_msg = args.commit_message or ''
        
        # Generate medical validation report
        report = validator.generate_medical_report(
            args.medical_impact, test_data, changed_files, commit_msg
        )
        
        if args.verbose:
            print(json.dumps(report, indent=2))
        else:
            print(f"Medical Safety Status: {report['overall_status']}")
            print(f"Safety Score: {report['medical_safety_score']}%")
            print(f"Impact Level: {report['medical_impact']}")
            if report['summary']['total_errors'] > 0:
                print(f"Errors Found: {report['summary']['total_errors']}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
        
        # Exit with error code if validation failed
        if report['overall_status'] != 'PASS':
            print(f"\n❌ Medical validation failed", file=sys.stderr)
            for validation_name, validation_result in report['validations'].items():
                if not validation_result.get('passed', True):
                    print(f"  - {validation_name}: FAILED", file=sys.stderr)
                    for error in validation_result.get('errors', []):
                        print(f"    • {error}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\n✅ Medical validation passed")
            
    except Exception as e:
        print(f"Error during medical validation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()