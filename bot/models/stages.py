from enum import Enum

class JobStage(Enum):
    RECEIVED = "received"
    QUEUED = "queued"

    FETCHING_INFO = "fetching_info"
    PROCESSING = "processing"

    SAVING = "saving"

    FINISHED = "finished"
    ERROR = "error"