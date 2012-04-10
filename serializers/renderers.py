from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.utils import simplejson as json
from django.utils.encoding import smart_unicode
from django.utils.xmlutils import SimplerXMLGenerator
import StringIO
try:
    import yaml
except ImportError:
    yaml = None


class BaseRenderer(object):
    """
    Defines the base interface that renderers should implement.
    """

    def render(obj, **opts):
        return str(obj)


class JSONRenderer(BaseRenderer):
    """
    Render a native python object into JSON.
    """
    def render(self, obj, **opts):
        indent = opts.pop('indent', None)
        sort_keys = opts.pop('sort_keys', False)

        return json.dumps(obj, cls=DateTimeAwareJSONEncoder,
                          indent=indent, sort_keys=sort_keys)


class YAMLRenderer(BaseRenderer):
    """
    Render a native python object into YAML.
    """
    def render(self, obj, **opts):
        indent = opts.pop('indent', None)

        return yaml.dump(obj, indent=indent)


class XMLRenderer(BaseRenderer):
    """
    Render a native python object into XML.
    Note that this renderer is included more by way of example,
    than as a proposed final XML renderer.
    """
    def render(self, obj, **opts):
        stream = StringIO.StringIO()

        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement("root", {})

        self._to_xml(xml, obj)

        xml.endElement("root")
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement("list-item", {})
                self._to_xml(xml, item)
                xml.endElement("list-item")

        elif isinstance(data, dict):
            # TODO: use iteritems unless sort_keys is set.
            for key, value in sorted(data.items()):
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_unicode(data))


if not yaml:
    YAMLRenderer = None