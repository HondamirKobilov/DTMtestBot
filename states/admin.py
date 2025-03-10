from aiogram.dispatcher.filters.state import State, StatesGroup


class ChannelAdding(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_name = State()


class ChannelModification(StatesGroup):
    waiting_for_new_id = State()
    waiting_for_new_name = State()


class SubjectAdding(StatesGroup):
    waiting_for_subject_name = State()


class VariantAdding(StatesGroup):
    waiting_for_variant_answer_key = State()
    waiting_for_variant_document = State()

class AddSubjectState(StatesGroup):
    waiting_for_subject_name = State()

class EditCompulsorySubjectState(StatesGroup):
    waiting_for_new_name = State()
class EditMainSubjectState(StatesGroup):
    waiting_for_new_name = State()
class UploadTestState(StatesGroup):
    waiting_for_file = State()
    waiting_for_docx = State()

class AddDiagnostikaState(StatesGroup):
    waiting_for_name = State()
    waiting_for_finished_at = State()

class EditDiagnostikaState(StatesGroup):
    name = State()
    waiting_for_finished_at = State()