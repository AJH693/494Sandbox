import json

import models


class Grader:

    def __init__(self):
        pass

    def calculate_correctness(self, response_id):
        task_response = models.TaskResponse.query.filter_by(id=response_id).first()
        response = json.loads(task_response.graded_response)
        correct = 0
        total_graded = 0
        total = len(response['manual_questions']) + len(response['automatic_questions'])
        for question in response['automatic_questions']:
            if question.get('not-graded'):
                total -= 1
                continue
            correct += 100 if question['correct'] else 0
            total_graded += 1
        for question in response['manual_questions']:
            if question.get('not-graded'):
                total -= 1
                continue
            correct += int(question['correctness']) if int(question.get('correctness', -1)) >= 0 else 0
            total_graded += 1 if int(question.get('correctness', -1)) >= 0 else 0
        task_response.graded = (total == total_graded)
        return int(float(correct) / total_graded) if total_graded else 0

    def grade_manual_question(self, response_id, question_id, correct,
                              category='correctness'):
        response = models.TaskResponse.query.filter_by(id=response_id).first()
        graded_response = json.loads(response.graded_response)
        for question in graded_response['manual_questions']:
            if question['questionID'] == question_id:
                question[category] = correct
        response.graded_response = json.dumps(graded_response)
        if category == 'correctness':
            correctness_grade = self.calculate_correctness(response_id)
            response.correctness_grade = correctness_grade
            models.db.session.commit()
            return correctness_grade

    def grade_automatic_questions(self, response_id):
        task_response = models.TaskResponse.query.filter_by(id=response_id).first()
        if task_response.graded_response:
            return
        response = json.loads(task_response.response)
        task = task_response.task
        task_questions = json.loads(task.questions)
        for question in response['automatic_questions']:
            for task_question in task_questions:
                if task_question['questionID'] == question['questionID']:
                    correctOption = task_question.get('correctOption')
                    correct = (question.get('selectedOption') == correctOption)
                    question['correctOption'] = correctOption
                    question['correct'] = correct
                    question['correctOptionText'] = task_question['correctOptionText']
        task_response.graded_response = json.dumps(response)
        task_response.correctness_grade = self.calculate_correctness(response_id)
        models.db.session.commit()
        return response['automatic_questions']

    def grade_supplementary_material(self, response_id):
        task_response = models.TaskResponse.query.filter_by(id=response_id).first()
        if task_response.graded_supplementary:
            return
        response_supplementary = json.loads(task_response.supplementary) if task_response.supplementary else {}
        graded_response = []
        task = task_response.task
        task_supplementary = json.loads(task.supplementary) if task.supplementary else {}
        sufficient_materials = 0
        for sup_id, sup_data in task_supplementary.items():
            time = response_supplementary.get(sup_id)
            graded_response.append({
                'time': time,
                'expected_time': sup_data.get('time'),
                'sufficient': time >= sup_data.get('time'),
                'id': sup_id,
                'title': sup_data.get('title')
            })
            sufficient_materials += 1 if time >= sup_data.get('time') else 0
        task_response.cognitive_grade = int(float(100 * sufficient_materials) / len(graded_response)) if graded_response else 0
        task_response.graded_supplementary = json.dumps(graded_response)
        models.db.session.commit()
