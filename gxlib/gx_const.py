import numpy as _np
import pandas as _pd
J2000origin = _np.datetime64('2000-01-01 12:00:00')

gf_df = _pd.DataFrame(
index = [
'PREM','PREM_disp','PREMd','PREM_compr','PREMc','PREM_disp_compr','PREMdc',
'STW105','STW105_disp','STW105d','STW105_compr','STW105c','STW105_disp_compr','STW105dc',
'S362ANI','S362ANI_disp','S362ANId','S362ANI_compr','S362ANIc','S362ANI_disp_compr','S362ANIdc'
        ],
data = _np.asarray([
['PREM','PREMd','PREMd','PREMc','PREMc','PREMdc','PREMdc',
'STW105','STW105d','STW105d','STW105c','STW105c','STW105dc','STW105dc',
'S362ANI','S362ANId','S362ANId','S362ANIc','S362ANIc','S362ANIdc','S362ANIdc'],
['C0','C0','C0','C0','C0','C0','C0',
'C1','C1','C1','C1','C1','C1','C1',
'C2','C2','C2','C2','C2','C2','C2'],
['dotted','dashed','dashed','dashdot','dashdot','solid','solid',
'dotted','dashed','dashed','dashdot','dashdot','solid','solid',
'dotted','dashed','dashed','dashdot','dashdot','solid','solid']
]).T,
columns=['em_short','color','linestyle'])
