import inspect
import urlparse

class ObjectPublisherURLParser(object):
    def __init__(self, page):
        self.linkmap = self._get_linkmap(page)
        urls = list(self.linkmap.keys())
        urls.sort()
        urls.reverse()
        self.urls = urls

    def parse_url(self, url):
        _, _, path, _, query, _ = urlparse.urlparse(url)

        prefix = find_longest_prefix(path, self.urls)
        page = self.linkmap[prefix]

        args_names, _, _, args_values = inspect.getargspec(page.index)
        args_values = args_values if args_values is not None else []

        args = self._get_args(path.replace(prefix, ''), args_names, args_values)
        kwargs = self._get_kwargs(query, args_names, args_values)

        return page, args, kwargs

    def _get_args(self, extra_path, args_names, args_values):
        path_args = [a for a in extra_path.split('/') if a]

        args_count = len(args_names) - len(args_values)
        args = path_args

        missing_args_count = len(args_names) - len(path_args) -1
        if missing_args_count > 0:
            args += [None] * missing_args_count
        elif missing_args_count < 0:
            raise HTTP404NotFound('{0} not found'.format(extra_path))

        return args[:args_count-1]

    def _get_kwargs(self, query, args_names, args_values):
        query_args = urlparse.parse_qs(query)

        for key, value in query_args.items():
            if isinstance(value, list) and len(value) == 1:
                query_args[key] = value[0]

        page_kwargs = {
            name: value
            for name, value in zip(reversed(args_names), reversed(args_values))
        }

        return {
            name: query_args.get(name, value)
            for name, value in page_kwargs.items()
        }



    def _get_linkmap(self, page, path=None, linkmap=None):
        linkmap = {} if linkmap is None else linkmap
        path = '' if path is None else path

        linkmap[path] = page

        for attr_name in dir(page):
            attr = getattr(page, attr_name)
            if is_page(attr):
                self._get_linkmap(attr, '/'.join((path, attr_name)), linkmap)

        try:
            page_url = path if path != '' else '/'
            page.set_url(page_url)
        except:
            pass

        return linkmap

def is_page(obj):
    return (
        not inspect.isclass(obj) and
        hasattr(obj, 'index') and
        inspect.ismethod(obj.index)
    )

def find_longest_prefix(string, prefixes):
    longest = ""

    for prefix in prefixes:
        if string.startswith(prefix):
            longest = prefix
            break

    return longest

class HTTP404NotFound(Exception):
    pass
