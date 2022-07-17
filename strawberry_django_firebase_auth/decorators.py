# Inspired by https://github.com/melvinkcx/graphql-utilities/blob/master/graphql_utilities/decorators.py

from functools import wraps

def one_time_middleware(resolve_func):
    """
    Make sure middleware is run only once,
    this is done by setting a flag in the `context` of `ResolverInfo`
    Example:
        class AuthenticationMiddleware:
            @one_time_middleware
            def resolve(self, next, root, info, *args, **kwargs):
                pass
    """
    @wraps(resolve_func)
    def wrapper(self, next, root, info, *args, **kwargs):
        decorator_name = "__{}_run__".format(self.__class__.__name__)

        if info.context is not None:
            if isinstance(info.context, dict) and not info.context.get(decorator_name, False):
                info.context[decorator_name] = True
                return resolve_func(self, next, root, info, *args, **kwargs)
            elif not isinstance(info.context, dict) and not getattr(info.context, decorator_name, False):
                setattr(info.context, decorator_name, True)
                return resolve_func(self, next, root, info, *args, **kwargs)

        return next(root, info, *args, **kwargs)

    return wrapper