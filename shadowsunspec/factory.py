# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/factory.ipynb (unless otherwise specified).

__all__ = ['list_to_indexdir', 'create_model', 'assemble_sunspec_model', 'assemble', 'ShadowSunspecEncoder',
           'NAMESPACE', 'encode']

# Cell
import json
import sunspec.core.device as device

# Cell
def list_to_indexdir(lst):
    '''
    Transforms a list into a dictionary with
    {list index: list value}

    lst: Any enumeratable object

    Example:
    >> list_to_indexdir(['a', {'b':1}])
    {0: 'a', 1: {'b': 1}}
    '''
    returnme = {}
    for index, item in enumerate(lst):
        returnme[index] = item
    return returnme

# Cell
def create_model(device_object, mid, repeating=None):
    #make a non-repeating model so that we can introspect the length of the repeating block
    model = device.Model(device=device_object, mid=mid)
    model.load()
    if repeating:
        mlen = None
        fixed_block, repeating_blocks = model.blocks
        mlen = fixed_block.len + repeating*repeating_blocks.len
        return device.Model(device=device_object, mid=mid, mlen=mlen)
    return device.Model(device=device_object, mid=mid)

def assemble_sunspec_model(model_definitions, device_object=None):
    dev = device_object or device.Device()
    for model_definition in model_definitions:
        curr_model = create_model(dev, **model_definition)
        curr_model.load()
        dev.add_model(curr_model)
    return dev
assemble = assemble_sunspec_model

# Cell
NAMESPACE = 'sunspec'
class ShadowSunspecEncoder(json.JSONEncoder):
    '''
    Recursively json encodes a sunspec model into a shadow-sunspec compliant object
    Note that if the top level object is a list you will not get a index-dir as defined above.

    This class returns an example dictionary.  It is made for communication purposes.
    It contains the datatype as the value instead of the actual modbus or canbus data.
    '''
    def default(self, obj):
        if isinstance(obj, device.Model):
            return self.encode_model(obj)
        elif isinstance(obj, device.Device):
            return self.encode_device(obj)
        elif isinstance(obj, device.Block):
            return self.encode_block(obj)
        elif isinstance(obj, device.Point):
            return self.encode_point(obj)
        else:
            raise ValueError("Cant encode {}".format(obj))

    def encode_device(self, device):
        return {NAMESPACE: list_to_indexdir(device.models_list)}

    def encode_model(self, model):
        model_dir = self.encode_blocks(model.blocks)
        model_dir['id'] = model.id
        return model_dir

    def encode_point(self, point):
        pt = point.point_type
        # !!! In the real shadow this dictionary will not contain the datatype !!!
        # !!! Instead it will have the value of the modbus register !!!
        return {pt.id: pt.type}

    def encode_points_list(self, points_list):
        points_dir = {}
        for point in points_list:
            points_dir.update(self.encode_point(point))
        return points_dir

    def encode_block(self, block):
        return self.encode_points_list(block.points_list)

    def encode_blocks(self, blocks):
        ''' blocks: List[device.Block]
        '''
        block_dir = {}
        fixed_block = blocks[0]
        assert fixed_block.type=='fixed'
        block_dir['fixed'] = fixed_block
        try:
            repeating_blocks = blocks[1:]
        except IndexError:
            repeating_blocks = []

        if repeating_blocks:
            block_dir['repeating'] = list_to_indexdir(repeating_blocks)

        return block_dir


# Cell
def encode(obj, as_obj=False):
    dumped = json.dumps(obj, cls=ShadowSunspecEncoder)
    if as_obj:
        return json.loads(dumped)
    else:
        return dumped