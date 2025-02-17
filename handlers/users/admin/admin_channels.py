from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import channels_manager
from data.texts import const_text
from filters import F
from keyboards.inline.inline_admin import channels_menu, edit_channel_menu
from loader import dp
from states.admin import ChannelAdding, ChannelModification


@dp.callback_query_handler(F.AdminFilter(), F.CallBackFilter("admin_manage_channels"), run_task=True)
@dp.callback_query_handler(F.AdminFilter(), text='admin_back_to_channels', run_task=True)
async def callback_manage_channels(call: types.CallbackQuery):
    await call.message.edit_text(const_text("admin_manage_channels_intro"), reply_markup=channels_menu())


@dp.callback_query_handler(F.AdminFilter(), text="admin_add_channel", run_task=True)
async def callback_add_channel(call: types.CallbackQuery):
    await ChannelAdding.waiting_for_channel_id.set()
    await call.message.edit_text(const_text("admin_enter_new_channel_id"), reply_markup=None)


@dp.message_handler(F.AdminFilter(), state=ChannelAdding.waiting_for_channel_id, run_task=True)
async def process_channel_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['channel_id'] = message.text

    await ChannelAdding.next()
    await message.answer(const_text("admin_enter_channel_name"))


@dp.message_handler(F.AdminFilter(), state=ChannelAdding.waiting_for_channel_name, run_task=True)
async def process_channel_name(message: types.Message, state: FSMContext):
    channel_name = message.text
    async with state.proxy() as data:
        channel_id = data['channel_id']

    channels_manager.add_channel(channel_id, channel_name)
    await state.finish()
    await message.answer(const_text("admin_channel_added").format(channel_name=channel_name, channel_id=channel_id))
    await message.answer(const_text("admin_manage_channels_intro"), reply_markup=channels_menu())


# @dp.callback_query_handler(F.AdminFilter(), lambda c: c.data and c.data.startswith('admin_edit_'), run_task=True)
# async def callback_edit_channel(call: types.CallbackQuery):
#     channel_id = call.data.replace('admin_edit_', '')
#     channel = channels_manager.get_channel_by_id(channel_id)
#     print(channel)
#     if not channel:
#         await call.answer(const_text("admin_channel_not_found"), show_alert=True)
#         return
#
#     await call.message.edit_text(
#         const_text("admin_channel_edit_prompt").format(channel_title=channel['title']),
#         reply_markup=edit_channel_menu(channel['id'])
#     )


@dp.callback_query_handler(F.AdminFilter(), lambda c: c.data and c.data.startswith('admin_delete_channel_'), run_task=True)
async def callback_delete_channel(call: types.CallbackQuery):
    channel_id = call.data.replace('admin_delete_channel_', '')
    channels_manager.remove_channel(channel_id)
    await call.answer(const_text("admin_channel_deleted"))
    await call.message.edit_reply_markup(reply_markup=channels_menu())


@dp.callback_query_handler(F.AdminFilter(), lambda c: c.data and c.data.startswith('admin_modify_'), run_task=True)
async def callback_modify_channel(call: types.CallbackQuery, state: FSMContext):
    channel_id = call.data.replace('admin_modify_', '')
    await state.update_data(old_channel_id=channel_id)
    await ChannelModification.waiting_for_new_id.set()
    await call.message.edit_text(const_text("admin_enter_new_channel_id_for_modification"), reply_markup=None)


@dp.message_handler(F.AdminFilter(), state=ChannelModification.waiting_for_new_id, run_task=True)
async def process_new_channel_id(message: types.Message, state: FSMContext):
    new_channel_id = message.text
    await state.update_data(new_channel_id=new_channel_id)
    await ChannelModification.next()
    await message.answer(const_text("admin_enter_new_channel_name"))


@dp.message_handler(F.AdminFilter(), state=ChannelModification.waiting_for_new_name, run_task=True)
async def process_new_channel_name(message: types.Message, state: FSMContext):
    new_channel_name = message.text
    user_data = await state.get_data()
    old_channel_id = user_data['old_channel_id']
    new_channel_id = user_data['new_channel_id']

    channels_manager.modify_channel(old_channel_id, new_channel_id, new_channel_name)
    await state.finish()
    await message.answer(
        const_text("admin_channel_modified").format(new_channel_name=new_channel_name, new_channel_id=new_channel_id),
        reply_markup=edit_channel_menu(new_channel_id)
    )
