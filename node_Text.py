import bpy, bmesh, mathutils
from bpy.props import StringProperty, EnumProperty, BoolProperty
from node_s import *
from util import *
import io
import csv
import collections

class SvTextInOp(bpy.types.Operator):
    """ Load CSV data """
    bl_idname = "node.sverchok_text_input"
    bl_label = "Sverchok text input"
    bl_options = {'REGISTER', 'UNDO'}
    
    name_objectin = StringProperty(name='text file name', description='Name of text buffer')
    
# how to find which node this operator belongs to?
# create operator for each and remove as needed?
 
    def execute(self, context):
        node = context.active_node
        if not type(node) is TextInNode:
            print("wrong type")
            return {'CANCELLED'}
        node.load()
        return {'FINISHED'}

    
class TextInNode(Node, SverchCustomTreeNode):
    ''' Text Input '''
    bl_idname = 'TextInNode'
    bl_label = 'Text Input'
    bl_icon = 'OUTLINER_OB_EMPTY'

# why is this shared between instances?

    csv_data = {}
    
    def avail_texts(self,context):
        texts = bpy.data.texts
# should be sorted       items = [(t.name,t.name,"") for t in sorted(texts, key = lambda t : t.name )]
        items = [(t.name,t.name,"") for t in texts]
        return items

    text = EnumProperty(items = avail_texts, name="Texts", 
                        description="Choose text file to load", update=updateNode)
    
    columns = BoolProperty(default=True, options={'ANIMATABLE'})
    names = BoolProperty(default=True, options={'ANIMATABLE'})
                                       
#    formatting options for future 
#    decimal = StringProperty(name="Decimal separator", default=".")
#    delimiter = StringProperty(name="Delimiter", default=",")
    

    def init(self, context):
        pass
                
    def draw_buttons(self, context, layout):
        layout.prop(self,"text","Text Select:")
        layout.prop(self,'columns','Columns')
        layout.prop(self,'names','Named fields?')
        layout.operator('node.sverchok_text_input', text='Load')

        # should be able to select external file

    def update(self):               
        for item in self.csv_data[self.name]:
            if item in self.outputs and len(self.outputs[item].links)>0:
                if not self.outputs[item].node.socket_value_update:
                    self.outputs[item].node.update()
                self.outputs[item].StringsProperty = str([self.csv_data[self.name][item]])
 
                        
    def update_socket(self, context):
        self.update()

    def load(self):
        
        csv_data = collections.OrderedDict() 
        
        if self.name in self.csv_data:
            del self.csv_data[self.name]
                    
        f = bpy.data.texts[self.text].as_string()
        # should be able to select external file
        reader = csv.reader(io.StringIO(f),delimiter=',')
        

        if self.columns:
            for i,row in enumerate(reader):         
                if i == 0: #setup names
                    if self.names:
                        for name in row:
                            tmp = name
                            print(name,row)
                            c = 1
                            while tmp in csv_data:
                                tmp = name+str(c)
                                c += 1
                                print(tmp,name,c)
    
                            csv_data[str(tmp)] = []
                        continue #first row is names    
                    else:
                        for j in range(len(row)):
                            csv_data["Col "+str(j)] = []
                # load data 
                              
                for j,name in enumerate(csv_data):
                    try:
                        csv_data[name].append(float(row[j]))   
                    except (ValueError, IndexError):
                        pass #discard strings other than first row
                        
        else:         #rows            
            for i,row in enumerate(reader):
                name = []
                out = []
                for j,obj in enumerate(row):
                    nr = []
                    try:
                        out.append(float(obj))   
                    except ValueError:
                        if j == 0 and self.names:
                            tmp = row[0]
                            c = 1    
                            while tmp in csv_data:
                                tmp = row[0]+str(c)
                                c += 1
                            name = tmp
                        else:
                            pass #discard strings other than first column

                if not name:
                    name = "Row "+ str(i)
                csv_data[name] = out   
                
        self.csv_data[self.name]=csv_data
        #remove sockets
        for out in self.outputs:
            self.outputs.remove(out)
        # create sockets with names, maybe implement update in future       
        for name in csv_data:
            self.outputs.new('StringsSocket', name, name)                 
                  
 


def register():
    bpy.utils.register_class(SvTextInOp)
    bpy.utils.register_class(TextInNode)
    
def unregister():
    bpy.utils.unregister_class(SvTextInOp)
    bpy.utils.unregister_class(TextInNode)

if __name__ == "__main__":
    register()



