class ExtractColumn2( Node ):
    """ Extract column based on str
    """
    header = ['']
    index = [0]

    def __init__(self):

        Node.__init__(self)

        funs= self.header
        self.add_input( name = "column", interface = IEnumStr(funs), value = funs[0])
       # self.add_input( name = "array" )
        self.add_output( name = "Column", interface = None)

    def __call__(self, inputs):
        col= self.get_input("column")
        i = self.index[self.header.index(col)]

        self.set_caption(col)

        return i,  self.header(i)

def ExtractColumn(ExtractColumn2):
    '''
    '''
    column_number = None;
    # write the node code here.
    header = """Iteration
    Day
    Hour
    Air Temperature
    Voxel
    Shaded Leaf Temperature
    Sunlit Leaf Temperature
    STAR_Direct
    STAR_Sky
    Shaded Leaf Photosynthesis
    Sunlit Leaf Photosynthesis
    Shaded Leaf Transpiration
    Sunlit Leaf Transpiration
    Shaded Leaf Surface Area
    Sunlit Leaf Surface Area
    Shaded_Leaf_StomatalConductance
    Sunlit_Leaf_StomatalConductance
    Leaf_Nitrogen
    """.split('\n')
    index = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    def __init__(self):

        column_number = ExtractColumn2.__init__(self)
