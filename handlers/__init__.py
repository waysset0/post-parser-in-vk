from aiogram import Router

def setup_handlers(dp):
    from .start import router as start_router
    from .add import router as add_router
    from .list import router as list_router
    from .remove import router as remove_router
    
    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(remove_router)