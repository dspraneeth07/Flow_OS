from fastapi_pagination import Page

from flowos.helpers.base_model import BaseModel
from flowos.services.database.models.flow.model import FlowRead
from flowos.services.database.models.folder.model import FolderRead


class FolderWithPaginatedFlows(BaseModel):
    folder: FolderRead
    flows: Page[FlowRead]
