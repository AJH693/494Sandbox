import json
import unittest

from mock import Mock
from mock import patch

import views

class TestGetThumbnail(unittest.TestCase): 
    def setUp(self):
        models = patch.object(views, "models")
        self.addCleanup(models.stop)
        self.models = models.start()

    def test_active_false(self):
        ret = views.get_thumbnail("")
        self.models.Thumbnail.query.filter_by.assert_called_with(id=3)

    def test_pdf_as_active_true(self):
        ret = views.get_thumbnail("pdf")
        self.models.Thumbnail.query.filter_by.assert_called_with(id=1)

    def test_txt_as_active_true(self):
        ret = views.get_thumbnail("txt")
        self.models.Thumbnail.query.filter_by.assert_called_with(id=2)

    def test_mp3_as_active_true(self):
        ret = views.get_thumbnail("mp3")
        self.models.Thumbnail.query.filter_by.assert_called_with(id=4)