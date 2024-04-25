# ********************************************************************************
# *         WARNING: This file is automatically generated by unasync.py.         *
# *                             DO NOT MANUALLY EDIT                             *
# *           Source File: patent_client/_async/epo/ops/family/api.py            *
# ********************************************************************************

from ..session import asession
from .model import Family


class FamilyAsyncApi:
    @classmethod
    def get_family(cls, number, doc_type="publication", format="docdb"):
        url = (
            f"http://ops.epo.org/3.2/rest-services/family/{doc_type}/{format}/{number}"
        )
        response = asession.get(url)
        return Family.model_validate(response.text)
