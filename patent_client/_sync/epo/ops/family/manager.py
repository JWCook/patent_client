# ********************************************************************************
# *         WARNING: This file is automatically generated by unasync.py.         *
# *                             DO NOT MANUALLY EDIT                             *
# *         Source File: patent_client/_async/epo/ops/family/manager.py          *
# ********************************************************************************

from patent_client.util.manager import Manager

from .api import FamilyAsyncApi
from .model import Family
from .schema import FamilySchema


class FamilyManager(Manager[Family]):
    __schema__ = FamilySchema

    def get(self, doc_number):
        return FamilyAsyncApi.get_family(doc_number, doc_type="publication", format="docdb")
