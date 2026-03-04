from argbox.context import Context
from argbox.dispatch import dispatcher


@dispatcher
def dispatch_on_type(*types: type):
    def validator(ctx: Context) -> bool:
        for i, type_ in enumerate(types):
            arg = ctx.get_arg(position=i)
            if not isinstance(arg, type_):
                return False
        return True

    return validator
