import os
from typing import Dict, List

class Pipeline:
    def __init__(self):
        self.tasks = [
            {
                'name': 'build',
                'cmd': ['make', 'build']
            },
            {
                'name': 'test',
                'cmd': ['make', 'test']
            },
            {
                'name': 'deploy',
                'cmd': ['make', 'deploy']
            }
        ]

    def run(self):
        for task in self.tasks:
            print(f"Running {task['name']} task")
            try:
                os.system(' && '.join(task['cmd']))
            except Exception as e:
                print(f"Error running {task['name']} task: {e}")

class SecurityScanner:
    def __init__(self):
        self.rules = [
            {
                'rule': 'SAST',
                'tool': 'bandit'
            },
            {
                'rule': 'DAST',
                'tool': 'ZAP'
            }
        ]

    def scan(self, pipeline: Pipeline):
        for rule in self.rules:
            print(f"Running {rule['rule']} scan using {rule['tool']}")
            try:
                if rule['rule'] == 'SAST':
                    os.system('bandit -r .')
                elif rule['rule'] == 'DAST':
                    os.system('./zap.sh')
            except Exception as e:
                print(f"Error running {rule['rule']} scan: {e}")

pipeline = Pipeline()
scanner = SecurityScanner()

pipeline.run()
scanner.scan(pipeline)
