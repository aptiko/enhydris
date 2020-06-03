from django.contrib.auth.models import AnonymousUser, Permission, User
from django.test import TestCase, override_settings

from model_mommy import mommy

from enhydris import models


class RulesTestCaseBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alice = User.objects.create_user(username="alice")
        cls.bob = User.objects.create_user(username="bob")
        cls.charlie = User.objects.create_user(username="charlie")
        cls.david = User.objects.create_user(username="david")

        cls.station = mommy.make(
            models.Station, creator=cls.alice, maintainers=[cls.bob]
        )
        cls.variable = mommy.make(models.Timeseries, gentity=cls.station)

        po = Permission.objects
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="view_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="change_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="delete_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="change_variable")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="delete_variable")
        )


class CommonTests:
    """Tests that will run both for ENHYDRIS_USERS_CAN_ADD_CONTENT=True and False.

    Below we have two TestCase subclasses (actually RulesTestCaseBase subclasses); one
    of them overrides setting ENHYDRIS_USERS_CAN_ADD_CONTENT to True, and the other one
    to False. This is a mixin containing tests that should have the same results in
    both cases.
    """

    def test_user_with_model_permissions_can_change_station(self):
        self.assertTrue(self.charlie.has_perm("enhydris.change_station", self.station))

    def test_user_with_model_permissions_can_delete_station(self):
        self.assertTrue(self.charlie.has_perm("enhydris.change_station", self.station))

    def test_user_with_model_permissions_can_change_variable(self):
        self.assertTrue(
            self.charlie.has_perm("enhydris.change_variable", self.variable)
        )

    def test_user_with_model_permissions_can_delete_variable(self):
        self.assertTrue(
            self.charlie.has_perm("enhydris.change_variable", self.variable)
        )

    def test_user_without_permissions_cannot_change_station(self):
        self.assertFalse(self.david.has_perm("enhydris.change_station", self.station))

    def test_user_without_permissions_cannot_delete_station(self):
        self.assertFalse(self.david.has_perm("enhydris.change_station", self.station))

    def test_user_without_permissions_cannot_change_variable(self):
        self.assertFalse(
            self.david.has_perm("enhydris.change_variable", self.variable)
        )

    def test_user_without_permissions_cannot_delete_variable(self):
        self.assertFalse(
            self.david.has_perm("enhydris.change_variable", self.variable)
        )


@override_settings(ENHYDRIS_USERS_CAN_ADD_CONTENT=True)
class RulesTestCaseWhenUsersCanAddContent(RulesTestCaseBase, CommonTests):
    def test_creator_can_change_station(self):
        self.assertTrue(self.alice.has_perm("enhydris.change_station", self.station))

    def test_creator_can_delete_station(self):
        self.assertTrue(self.alice.has_perm("enhydris.delete_station", self.station))

    def test_creator_can_change_variable(self):
        self.assertTrue(
            self.alice.has_perm("enhydris.change_variable", self.variable)
        )

    def test_creator_can_delete_variable(self):
        self.assertTrue(
            self.alice.has_perm("enhydris.delete_variable", self.variable)
        )

    def test_maintainer_can_change_station(self):
        self.assertTrue(self.bob.has_perm("enhydris.change_station", self.station))

    def test_maintainer_cannot_delete_station(self):
        self.assertFalse(self.bob.has_perm("enhydris.delete_station", self.station))

    def test_maintainer_can_change_variable(self):
        self.assertTrue(
            self.bob.has_perm("enhydris.change_variable", self.variable)
        )

    def test_maintainer_can_delete_variable(self):
        self.assertTrue(
            self.bob.has_perm("enhydris.delete_variable", self.variable)
        )


@override_settings(ENHYDRIS_USERS_CAN_ADD_CONTENT=False)
class RulesTestCaseWhenUsersCannotAddContent(RulesTestCaseBase, CommonTests):
    def test_creator_is_irrelevant_for_change_station(self):
        self.assertFalse(self.alice.has_perm("enhydris.change_station", self.station))

    def test_creator_is_irrelevant_for_delete_station(self):
        self.assertFalse(self.alice.has_perm("enhydris.delete_station", self.station))

    def test_creator_is_irrelevant_for_change_variable(self):
        self.assertFalse(
            self.alice.has_perm("enhydris.change_variable", self.variable)
        )

    def test_creator_is_irrelevant_for_delete_variable(self):
        self.assertFalse(
            self.alice.has_perm("enhydris.delete_variable", self.variable)
        )

    def test_maintainer_is_irrelevant_for_change_station(self):
        self.assertFalse(self.bob.has_perm("enhydris.change_station", self.station))

    def test_maintainer_is_irrelevant_for_delete_station(self):
        self.assertFalse(self.bob.has_perm("enhydris.delete_station", self.station))

    def test_maintainer_is_irrelevant_for_change_variable(self):
        self.assertFalse(
            self.bob.has_perm("enhydris.change_variable", self.variable)
        )

    def test_maintainer_is_irrelevant_for_delete_variable(self):
        self.assertFalse(
            self.bob.has_perm("enhydris.delete_variable", self.variable)
        )


class ContentRulesTestCaseBase(TestCase):
    """Test case base for time series data and file content."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alice = User.objects.create_user(username="alice")
        cls.bob = User.objects.create_user(username="bob")
        cls.charlie = User.objects.create_user(username="charlie")
        cls.david = User.objects.create_user(username="david")
        cls.anonymous = AnonymousUser()

        cls.station = mommy.make(
            models.Station, creator=cls.alice, maintainers=[cls.bob]
        )
        cls.variable = mommy.make(models.Timeseries, gentity=cls.station)
        cls.gentityfile = mommy.make(models.GentityFile, gentity=cls.station)

        po = Permission.objects
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="view_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="change_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="delete_station")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="change_variable")
        )
        cls.charlie.user_permissions.add(
            po.get(content_type__app_label="enhydris", codename="delete_variable")
        )


@override_settings(ENHYDRIS_OPEN_CONTENT=True)
class ContentRulesWhenContentIsOpenTestCase(ContentRulesTestCaseBase):
    def test_anonymous_can_download_timeseries(self):
        self.assertTrue(
            self.anonymous.has_perm("enhydris.view_timeseries_data", self.variable)
        )

    def test_anonymous_can_download_gentity_file(self):
        self.assertTrue(
            self.anonymous.has_perm(
                "enhydris.view_gentityfile_content", self.variable
            )
        )


@override_settings(ENHYDRIS_OPEN_CONTENT=False)
class ContentRulesWhenContentIsNotOpen(ContentRulesTestCaseBase):
    def test_anonymous_cannot_download_variable(self):
        self.assertFalse(
            self.anonymous.has_perm("enhydris.view_timeseries_data", self.variable)
        )

    def test_anonymous_cannot_download_gentity_file(self):
        self.assertFalse(
            self.anonymous.has_perm(
                "enhydris.view_gentityfile_content", self.variable
            )
        )

    def test_logged_on_can_download_timeseries(self):
        self.assertTrue(
            self.david.has_perm("enhydris.view_timeseries_data", self.variable)
        )

    def test_logged_on_can_download_gentity_file(self):
        self.assertTrue(
            self.david.has_perm("enhydris.view_gentityfile_content", self.variable)
        )
