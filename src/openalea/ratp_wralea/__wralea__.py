
# This file has been generated at Mon Dec 07 14:49:50 2015

from openalea.core import *


__name__ = 'PyRATP'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.9.0'
__authors__ = ''
__institutes__ = None
__icon__ = 'icon.png'


__all__ = ['ratp_PlantGL2VTK', 'ratp_can2riri', 'ratp_RATP2VTK_Leaves', 'ExtractLight_ExtractLight', 'ExtractLight_ExtractVoxels', 'ratp_read_grid', 'ExtractVar_ExtractVar', 'ratp_DoAll', 'ratp_fill_grid', 'ratp_DoIrradiation', 'Plot3DRATP_Plot3DRATP', 'ratp_read_vgx', 'ratp_ExtractTime', 'ratp_extract_leaves', 'ratp_read_vegetation', 'ratp_RATPVOXELS2VTK', 'ratp_Nallocate', 'ratp_read_micrometeo', 'ratp_read_skyvault']



ratp_can2riri = Factory(name='can2riri',
                authors=' (wralea authors)',
                description='can2riri',
                category='simulation, ecophysiology',
                nodemodule='ratp',
                nodeclass='can2riri',
                inputs=[{'interface': IFileStr(filter="*.can", save=False), 'name': 'filename', 'value': None, 'desc': '3D can file'}],
                outputs=[{'interface': IInt, 'name': 'entity', 'desc': ''}, {'interface': IFloat, 'name': 'x', 'desc': ''}, {'interface': IFloat, 'name': 'y', 'desc': ''}, {'interface': IFloat, 'name': 'z', 'desc': ''}, {'interface': IFloat, 'name': 's', 'desc': ''}, {'interface': IFloat, 'name': 'n', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )

ratp_PlantGL2VTK = Factory(name='PlantGL2VTK',
                authors=' (wralea authors)',
                description='Paraview file',
                category='data i/o',
                nodemodule='ratp',
                nodeclass='PlantGL2VTK',
                inputs=[{'interface': ISequence, 'name': 'Scene', 'value': None, 'desc': ''}, {'interface': ISequence, 'name': 'Variable', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'VariableName', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'OutputFileName', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'VTK File', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )


ratp_RATP2VTK_Leaves = Factory(name='RATP2VTK_Leaves',
                authors=' (wralea authors)',
                description='Paraview file',
                category='data i/o',
                nodemodule='ratp',
                nodeclass='RATP2VTK',
                inputs=[{'interface': ISequence, 'name': 'Scene', 'value': None, 'desc': ''}, {'interface': ISequence, 'name': 'Variable', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'VariableName', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'OutputFileName', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'VTK File', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ExtractLight_ExtractLight = Factory(name='ExtractLight',
                authors=' (wralea authors)',
                description='Extract a Variable from RATP Voxel output',
                category='data processing',
                nodemodule='ExtractLight',
                nodeclass='ExtractLight',
                inputs=[{'interface': None, 'name': 'Elt2Voxel', 'value': None, 'desc': ''}, {'interface': None, 'name': 'RATPOutput', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Day', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Hour', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Variable', 'value': None, 'desc': 'Numero colonne de la variable choisie'}],
                outputs=[{'interface': None, 'name': 'Var To Plot', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ExtractLight_ExtractVoxels = Factory(name='ExtractVoxels',
                authors=' (wralea authors)',
                description='Extract PAR from RATP output',
                category='data processing',
                nodemodule='ExtractLight',
                nodeclass='ExtractVoxels',
                inputs=[{'interface': None, 'name': 'RATPOutput', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Day', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Hour', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'Variable', 'value': None, 'desc': 'Numero colonne de la variable choisie'}],
                outputs=[{'interface': None, 'name': 'PAR', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_grid = Factory(name='read grid',
                authors=' (wralea authors)',
                description='Build a RATP Grid',
                category='simulation, ecophysiology',
                nodemodule='ratp',
                nodeclass='read_grid',
                inputs=[{'interface': IFileStr(filter="*.grd", save=False), 'name': 'filename', 'value': None, 'desc': '3d Grid file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule='WidgetUiRATP_Grid',
                widgetclass='ClassUiRATP_Grid',
               )




ExtractVar_ExtractVar = Factory(name='ExtractVar',
                authors=' (wralea authors)',
                description='',
                category='data i/o',
                nodemodule='ExtractVar',
                nodeclass='ExtractVar',
                inputs=[{'interface': ISlice, 'name': 'IN1', 'value': None, 'desc': 'dfgd'}, {'interface': None, 'name': 'IN2', 'value': None, 'desc': 'dgdg'}],
                outputs=[{'interface': IInt, 'name': 'Column', 'desc': 'dfgfd'}, {'interface': IStr, 'name': 'Name', 'desc': 'dfgdfg'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_DoAll = Factory(name='do_all',
                authors=' (wralea authors)',
                description='run RATP',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='DoAll',
                inputs=[{'interface': ISequence, 'name': 'inputs', 'value': None, 'desc': ''}],
                outputs=[{'name': 'time_spatial', 'desc': 'time evolution for each voxel'}, {'name': 'tree', 'desc': 'time evolution for each voxel'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_fill_grid = Factory(name='fill grid',
                authors=' (wralea authors)',
                description='fill a RATP Grid with vegetation',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='fill_grid',
                inputs=[{'interface': IInt, 'name': 'entity', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'x', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'y', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'z', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 's', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'n', 'value': None, 'desc': ''}, {'interface': None, 'name': 'grid', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}, {'interface': None, 'name': 'Elt2Voxels', 'desc': ''}, {'interface': ISequence, 'name': 'Scene', 'desc': 'Colored Scene  '}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_DoIrradiation = Factory(name='ratp_radiation',
                authors=' (wralea authors)',
                description='run RATP - irradiation calculation only',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='DoIrradiation',
                inputs=[{'interface': ISequence, 'name': 'inputs', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'RATP_Output', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




Plot3DRATP_Plot3DRATP = Factory(name='Plot3DRATP',
                authors=' (wralea authors)',
                description='',
                category='visualisation',
                nodemodule='Plot3DRATP',
                nodeclass='Plot3DRATP',
                inputs=[{'interface': ISequence, 'name': 'Scene', 'value': None, 'desc': ''}, {'interface': ISequence, 'name': 'Color', 'value': None, 'desc': ''}],
                outputs=[{'interface': ISequence, 'name': 'Scene', 'desc': 'Colored Scene  '}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_vgx = Factory(name='plant from vegestar',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_vgx',
                inputs=[{'interface': IFileStr(filter="*.vgx", save=False), 'name': 'filename', 'value': None, 'desc': 'Vegestar 3d Grid file'}, {'interface': IFloat, 'name': 'CoeffAll', 'value': None, 'desc': ''}],
                outputs=[{'interface': IInt, 'name': 'entity', 'desc': ''}, {'interface': IFloat, 'name': 'x', 'desc': ''}, {'interface': IFloat, 'name': 'y', 'desc': ''}, {'interface': IFloat, 'name': 'z', 'desc': ''}, {'interface': IFloat, 'name': 's', 'desc': ''}, {'interface': IFloat, 'name': 'n', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_ExtractTime = Factory(name='extract time',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='ExtractTime',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )




ratp_extract_leaves = Factory(name='extract leaves',
                authors=' (wralea authors)',
                description='',
                category='Mtg, light',
                nodemodule='ratp',
                nodeclass='extract_leaves',
                inputs=[{'name': 'mtg', 'desc': 'MTG file'}, {'interface': 'IFloat', 'name': 'scaling factor', 'value': 100}, {'interface': 'IFloat', 'name': 'nitrogen', 'value': 2.0}],
                outputs=[{'name': 'leaves_id', 'desc': 'vertex id for leaves '}, {'name': 'entity', 'desc': 'the vegetation type'}, {'name': 'X', 'desc': 'X coordinate'}, {'name': 'Y', 'desc': 'Y coordinate'}, {'name': 'Z', 'desc': 'Z coordinate'}, {'name': 'leaf area', 'desc': 'leaf area'}, {'name': 'leaf nitrogen', 'desc': 'leaf nitrogen'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_vegetation = Factory(name='read_vegetation',
                authors=' (wralea authors)',
                description='read the vegetation files',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_vegetation',
                inputs=[{'interface': IFileStr(filter="*.vfn", save=False), 'name': 'filename', 'value': None, 'desc': 'Vegetation file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule='WidgetUiRATP_Vege',
                widgetclass='ClassUiRATP_Vege',
               )




ratp_RATPVOXELS2VTK = Factory(name='RATPVOXELS2VTK',
                authors=' (wralea authors)',
                description='Paraview file',
                category='data i/o',
                nodemodule='ratp',
                nodeclass='RATPVOXELS2VTK',
                inputs=[{'interface': ISequence, 'name': 'Scene', 'value': None, 'desc': ''}, {'interface': ISequence, 'name': 'Variable', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'VariableName', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'OutputFileName', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'VTK File', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_Nallocate = Factory(name='Nallocate',
                authors=' (wralea authors)',
                description='allocate the Nitrogen',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='Nallocate',
                inputs=[{'interface': ISequence, 'name': 'inputs', 'value': None, 'desc': ''}, {'interface': ISequence, 'name': 'Variable', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'aNA', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'bNA', 'value': None, 'desc': ''}],
                outputs=[{'interface': ISequence, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_micrometeo = Factory(name='read_micrometeo',
                authors=' (wralea authors)',
                description='read the micrometeo files',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_micrometeo',
                inputs=[{'interface': IFileStr(filter="*.mto", save=False), 'name': 'filename', 'value': None, 'desc': 'Micrometeo file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_skyvault = Factory(name='read_skyvault',
                authors=' (wralea authors)',
                description='read the skyvault file',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_skyvault',
                inputs=[{'interface': IFileStr(filter="*.skv", save=False), 'name': 'filename', 'value': None, 'desc': 'Skywvault file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




