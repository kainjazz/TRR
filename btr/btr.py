import requests
from pprint import pprint
from behave.reporter.base import Reporter
import yaml
from behave.model import ScenarioOutline


class TReporter(Reporter):
    STATUS_PASSED = 1
    STATUS_BLOCKED = 2
    STATUS_UNTESTED = 3
    STATUS_RETEST = 4
    STATUS_FAILED = 5
    show_failed_cases = True

    STATUS_MAPS = {
        'passed': STATUS_PASSED,
        'failed': STATUS_FAILED,
        'skipped': STATUS_UNTESTED,
        'undefined': STATUS_UNTESTED,
        'executing': STATUS_UNTESTED,
        'untested': STATUS_UNTESTED,
    }

    def __init__(self):
        self.username = ''
        self.password = ''
        self.url = ""
        self.project = 0
        self.section_id = 0
        self.run_id = 0
        self.testrail_client = ''

    def feature(self, feature):
        self.load_yaml()
        self.section_id = self.search_section(feature.name)
        cases = []

        for case in feature.scenarios:
            if isinstance(case, ScenarioOutline):
                scenario_part_ids = [
                    (self.search_test_case(scenario_part.steps,
                                           self.section_id,
                                           scenario_part.name),
                     scenario_part)
                    for scenario_part in case]
                cases += scenario_part_ids
            else:
                case_id = self.search_test_case(case.steps, self.section_id, case.name)
                cases.append((case_id, case))
        run_name = feature.name+': '+feature.scenarios[0].name
        self.run_id = self.create_test_run(cases, self.section_id, run_name)
        for case_id, case in cases:
            self.send_result(case_id, self.run_id, case.steps, case.status.name)

    def load_yaml(self):
        with open("testrail.yml", 'r')as stream:
            try:
                config = yaml.load(stream)
                self.url = config['base_url']
                self.username = config['username']
                self.password = config['password']
                self.project = config['project_id']
                self.testrail_client = 'http://' + self.username + ':' + self.password + '@' + self.url + '/'
                return config
            except yaml.YAMLError:
                pprint('Конфиг не найден')

    def search_section(self, section_name):

        uri = 'index.php?/api/v2/get_sections/' + str(self.project)

        headers = {
            'Content-Type': "application/json",
        }

        response = requests.request("GET", self.testrail_client + uri, headers=headers)
        sections_list = response.json()
        sections_dict_id = []
        sections_dict_names = []
        for sections in sections_list:
            sections_dict_id.append(sections['id'])
            sections_dict_names.append(sections['name'])
        if section_name in sections_dict_names:
            section_id = sections_dict_id[sections_dict_names.index(section_name)]
            pprint('Найдена секция ' + section_name + ' section_id= ' + str(section_id))
            return section_id
        else:
            raise Exception('Секция не найдена, создайте секцию')

    def send_result(self, case_id, run_id, steps, run_status):
        uri = 'index.php?/api/v2/add_result_for_case/' + str(run_id) + '/' + str(case_id)
        headers = {
            'Content-Type': "application/json",
        }
        body = {"status_id": self.STATUS_MAPS[run_status],
                "custom_step_results": [
                    {
                        "content": step.name,
                        "status_id": self.STATUS_MAPS[step.status.name],
                        "comment": 'comment',
                        "actual": step.exception.__str__()
                    } for step in steps
                ]}
        response = requests.request("POST", self.testrail_client + uri, json=body, headers=headers)
        if response.status_code == 200:
            pprint("Отчет отправлен")
        else:
            raise Exception('Ошибка: Отчет не отправлен')

    def search_test_case(self, steps, section_id, test_case_name):
        steps = ['{} {}'.format(data.keyword, data.name) for data in steps]
        project = self.project
        uri = 'index.php?/api/v2/get_cases/' + str(project) + '&section_id=' + str(section_id)
        headers = {
            'Content-Type': "application/json",
        }
        response = requests.request("GET", self.testrail_client + uri, headers=headers)
        if not response.json():
            return self.create_test_case(steps, section_id, test_case_name)
        case_list = response.json()
        case_lists = []
        case_ids = []
        for test_case in case_list:
            custom_step_list = test_case['custom_steps_separated']
            step_names = [i['content'] for i in custom_step_list]
            case_lists.append(step_names)
            case_ids.append(test_case['id'])
        if not steps in case_lists:
            return self.create_test_case(steps, section_id, test_case_name)
        else:
            case_id = case_ids[case_lists.index(steps)]
            pprint('Получен тесткейс ' + str(case_id))
            if case_id == 1488:
                raise Exception(
                    '░░░░░░░░░░░░░░░░░░░░░\n░░░░░░░░░░░░▄▀▀▀▀▄░░░\n░░░░░░░░░░▄▀░░▄░▄░█░░\n░▄▄░░░░░▄▀░░░░▄▄▄▄█░░\n█░░▀▄░▄▀░░░░░░░░░░█░░\n░▀▄░░▀▄░░░░█░░░░░░█░░\n░░░▀▄░░▀░░░█░░░░░░█░░\n░░░▄▀░░░░░░█░░░░▄▀░░░\n░░░▀▄▀▄▄▀░░█▀░▄▀░░░░░\n░░░░░░░░█▀▀█▀▀░░░░░░░\n░░░░░░░░▀▀░▀▀░░░░░░░░')
            return case_id

    def create_test_case(self, steps, section_id, test_case_name):
        uri = 'index.php?/api/v2/add_case/' + str(section_id)
        body = {
            "title": test_case_name,
            "template_id": 2,

            "custom_steps_separated": [{"content": step_definition,
                                        'expected': 'In step definition'} for step_definition in steps]
        }
        response = requests.request("POST", self.testrail_client + uri, json=body)
        case_sum = response.json()
        case_id = case_sum['id']
        if case_id == 1488:
            raise Exception(
                '░░░░░░░░░░░░░░░░░░░░░\n░░░░░░░░░░░░▄▀▀▀▀▄░░░\n░░░░░░░░░░▄▀░░▄░▄░█░░\n░▄▄░░░░░▄▀░░░░▄▄▄▄█░░\n█░░▀▄░▄▀░░░░░░░░░░█░░\n░▀▄░░▀▄░░░░█░░░░░░█░░\n░░░▀▄░░▀░░░█░░░░░░█░░\n░░░▄▀░░░░░░█░░░░▄▀░░░\n░░░▀▄▀▄▄▀░░█▀░▄▀░░░░░\n░░░░░░░░█▀▀█▀▀░░░░░░░\n░░░░░░░░▀▀░▀▀░░░░░░░░')

        pprint('Создан новый тесткейс ' + str(case_id))
        return case_id

    def create_test_run(self, cases, section_id, section_name):
        project = self.project
        uri = 'index.php?/api/v2/add_run/' + str(project)
        headers = {
            'Content-Type': "application/json",
        }
        body = {
            "suite_id": section_id,
            "name": section_name,
            "include_all": False,
            "case_ids": [case_id for case_id, musor in cases]
        }
        response = requests.request("POST", self.testrail_client + uri, json=body, headers=headers)
        data = response.json()
        run_id = data['id']
        if response.status_code == 200:
            pprint('Создан Тест Ран ' + section_name + ' ' + str(run_id))
            return run_id
        else:
            raise AssertionError('Еггог')

        pass

    def end(self):
        pass
