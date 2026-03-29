"""Tests for quest system."""
import pytest
from game.quest.quest import Quest, QuestObjective, QuestStatus, QuestManager


class TestQuestObjective:
    def test_objective_creation(self):
        obj = QuestObjective("Kill 5 wolves", required=5)
        assert obj.required == 5
        assert obj.current == 0
        assert obj.is_complete is False

    def test_objective_progress(self):
        obj = QuestObjective("Kill 5 wolves", required=5)
        obj.progress(3)
        assert obj.current == 3
        assert obj.is_complete is False

    def test_objective_complete(self):
        obj = QuestObjective("Kill 5 wolves", required=5)
        obj.progress(5)
        assert obj.is_complete is True

    def test_objective_no_overflow(self):
        obj = QuestObjective("Kill 5 wolves", required=5)
        obj.progress(10)
        assert obj.current == 5


class TestQuest:
    def test_quest_creation(self):
        q = Quest(name="Main Quest")
        assert q.name == "Main Quest"
        assert q.status == QuestStatus.INACTIVE

    def test_quest_start(self):
        q = Quest(name="Quest")
        q.start()
        assert q.is_active is True

    def test_quest_complete(self):
        q = Quest(name="Quest")
        obj = QuestObjective("Do thing", required=1)
        q.add_objective(obj)
        q.start()
        obj.progress(1)
        q.check_completion()
        assert q.is_complete is True

    def test_quest_fail(self):
        q = Quest(name="Quest")
        q.start()
        q.fail()
        assert q.status == QuestStatus.FAILED

    def test_on_complete_callback(self):
        called = []
        q = Quest(name="Quest")
        obj = QuestObjective("Do thing", required=1)
        q.add_objective(obj)
        q.on_complete(lambda: called.append(True))
        q.start()
        obj.progress(1)
        q.check_completion()
        assert called == [True]

    def test_incomplete_quest(self):
        q = Quest(name="Quest")
        obj = QuestObjective("Kill 5", required=5)
        q.add_objective(obj)
        q.start()
        obj.progress(3)
        q.check_completion()
        assert q.is_complete is False


class TestQuestManager:
    def test_register_and_get(self):
        qm = QuestManager()
        q = Quest(name="Quest1")
        qm.register(q)
        assert qm.get("Quest1") is q

    def test_start_quest(self):
        qm = QuestManager()
        q = Quest(name="Quest1")
        qm.register(q)
        assert qm.start("Quest1") is True
        assert q.is_active is True

    def test_get_active(self):
        qm = QuestManager()
        q1 = Quest(name="Q1")
        q2 = Quest(name="Q2")
        qm.register(q1)
        qm.register(q2)
        qm.start("Q1")
        assert q1 in qm.get_active()
        assert q2 not in qm.get_active()
