
import os as _os
import sys as _sys

import numpy as _np
import pandas as _pd

from netCDF4 import Dataset as NetCDFFile

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

PYGCOREPATH = "{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'], _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0, PYGCOREPATH)

from gxlib.gx_hardisp import blq2hardisp
from gxlib.gx_aux import get_chalmers


from gxlib.gx_aux import blq2blq_df, norm_table, names2labels

def get_center(staDb_df,coeff=0.1,proportions=None):
    lons = staDb_df['LON'];lats = staDb_df['LAT']
    lon_min = _np.min(lons);lon_max = _np.max(lons); lon_range = lon_max - lon_min
    lat_min = _np.min(lats);lat_max = _np.max(lats); lat_range = lat_max - lat_min
    
    crnrs = _pd.DataFrame([[lon_min-lon_range*coeff,lat_min-lat_range*coeff,lon_max+lon_range*coeff,lat_max+lat_range*coeff],],columns=['llcrnrlon','llcrnrlat','urcrnrlon','urcrnrlat'])
    
#     width = crnrs['urcrnrlon']-crnrs['llcrnrlon']
#     height = crnrs['urcrnrlat']-crnrs['llcrnrlat']

    center = [(crnrs['urcrnrlon']+crnrs['llcrnrlon'])/2, (crnrs['urcrnrlat']+crnrs['llcrnrlat'])/2]
#     return center , width, height
    return center

def gen_corners(center_lon,center_lat, width,height):
    llcrnrlat= center_lat-width/2
    urcrnrlat= center_lat+width/2
    llcrnrlon= center_lon - height/2
    urcrnrlon= center_lon + height/2
    if urcrnrlon[0]>180:
        delta = urcrnrlon[0]-180
        urcrnrlon[0] = 180
        llcrnrlon[0] -= delta
    return llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon


def plot_shapefiles(m,ax,faults=True,countour_only=False):
        tvz_zoom = m.readshapefile('/home/bogdanm/Desktop/TVZ_line/TVZ', 'TVZ', drawbounds = True,ax=ax)
        tvz_zoom[-1].set_linestyle('dotted')
        #polygon of TVZ
        if not countour_only:
            tvz_poly_zoom = m.readshapefile('/home/bogdanm/Desktop/TVZ_line/TVZ_FeatureToPolygon', 'TVZ_zone',drawbounds=True,zorder=20,linewidth=0.05,color='0.1',ax=ax)
            tvz_poly_zoom[-1].set_facecolors(['r'])
            tvz_poly_zoom[-1].set_alpha(0.05)
            tvz_old_new = m.readshapefile('/home/bogdanm/Desktop/TVZ_line/TVZ_old_new', 'TVZ_old_new', drawbounds = True,ax=ax,color='0.1')
            tvz_old_new[-1].set_linestyle('--')
            tvz_zones = m.readshapefile('/home/bogdanm/Desktop/TVZ_line/TVZ_zones_bounds', 'TVZ_zones', drawbounds = True,ax=ax,color='0.1')
            tvz_zones[-1].set_linestyle('--')
        if faults:
            m.readshapefile('/home/bogdanm/Desktop/NZAFD_2d/NZAFD_2d_2', 'faults',drawbounds=True,zorder=2,linewidth=0.1,color='red')

def plot_dataset_map(project_name,fontsize=12,filename=None,constituent='M2',custom_blq_path=None,grid_max=65,grid=True,vectors=True,custom_stations_list=None,
                     normalize = True,
                     resolution='i',
                     window1=(None,None),
                     window2=None,
                     size = 10,
                     dpi=72,
                     width=10,
                     label_sites = True,
                     crnrs_coeff = 0.1,
                     otl_res_coeff = 3000,
                     title = 'title',
                     alpha_ellipse = 0.1,
                     arrow_width = 400,
                     ellipses=True,
                     components = ['up','east','north'],
                     proportion=1,
                     stations_left = ['DUNT','QUAR'],
                     stations_down=['WAKA'],
                     stations_zoomed = False,
                     width_zoomed=5,
                     proportion_zoomed=1,
                     constellations = ['GPS','GLONASS','GPS+GLONASS'],
                     ocn_netcdf_path = '/array/bogdanm/Products/otl/TPXO.7.2-displacements/RADI_amp.m2'):
    staDb_path = project_name.staDb_path
    
    staDb_df = get_chalmers(staDb_path,as_df=True)
    
    if custom_stations_list is not None:
        staDb_df = staDb_df[_np.isin(staDb_df['SITE'],custom_stations_list)]
        
    center = get_center(staDb_df,crnrs_coeff)
    height = width * proportion
    llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon = gen_corners(center_lat=center[1],center_lon=center[0],height=height,width=width)
    print(llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon)

    cmap = cm.get_cmap('PuBu')
    colors = _pd.DataFrame(['C0','C1','C2'],index = ['GPS','GLONASS','GPS+GLONASS'],columns=['color'])
    
    if len(constellations) == 1 and constellations[0] == 'GPS': 
        gps_only=True
        print('Found only GPS so gps_only set to True')
    else:
        gps_only = False
        print('gps_only set False')
        

#         x_otl,y_otl,semiAxisA,semiAxisP,phase = norm_table(project_name.analyze_gps(begin=begin,end=end),custom_blq_path=custom_blq_path,normalize=normalize,gps_only=gps_only)
    if gps_only:
        x_otl,y_otl,semiAxisA,semiAxisP,phase = norm_table(project_name.analyze_gps(begin=window1[0],end=window1[1]),custom_blq_path=custom_blq_path,normalize=normalize,gps_only=True)
        if window2 is not None:
            x_otl2,y_otl2,semiAxisA2,semiAxisP2,phase2 = norm_table(project_name.analyze_gps(begin=window2[0],end=window2[1]),custom_blq_path=custom_blq_path,normalize=normalize,gps_only=True)
            x_otl -=x_otl2
            y_otl -=y_otl2
    else:
        x_otl,y_otl,semiAxisA,semiAxisP,phase = norm_table(project_name.analyze(begin=window1[0],end=window1[1]),custom_blq_path=custom_blq_path,normalize=normalize,gps_only=False)
        
        if window2 is not None:
            x_otl2,y_otl2,semiAxisA2,semiAxisP2,phase2 = norm_table(project_name.analyze(begin=window2[0],end=window2[1]),custom_blq_path=custom_blq_path,normalize=normalize,gps_only=False)
            x_otl -=x_otl2
            y_otl -=y_otl2

    fig = plt.figure(figsize=(size,size),dpi=dpi)
    for component in components:
        ax = plt.subplot(111)
        if title:
            ax.set_title('{} {}$\degree$'.format(title,str(project_name.ElMin)) 
                 + (' | {}'.format(_os.path.basename(custom_blq_path)) if custom_blq_path is not None else ''),pad=20)
    #     m = Basemap(resolution='i',projection='merc', llcrnrlon=crnrs['llcrnrlon'],llcrnrlat=crnrs['llcrnrlat'],urcrnrlon=crnrs['urcrnrlon'],urcrnrlat=crnrs['urcrnrlat'],lat_ts=51.0)
        m = Basemap(resolution=resolution,projection='merc', llcrnrlat=llcrnrlat,urcrnrlat=urcrnrlat,llcrnrlon=llcrnrlon,urcrnrlon=urcrnrlon,lat_ts=45.0)
#         m.drawcountries(linewidth=0.5,color='grey',zorder=1)
        m.drawcoastlines(linewidth=0.5,color='grey',zorder=1)
        m.fillcontinents(color='0.95',lake_color='0.75')
        # m.etopo()

        m.drawparallels(_np.arange(-60.,0,5.),labels=[1,0,0,0],color='black',dashes=[1,0],labelstyle='',linewidth=0.2,zorder=2) # draw parallels
        m.drawmeridians(_np.arange(160.,180.,5.),labels=[0,1,1,0],color='black',dashes=[1,0],labelstyle='',linewidth=0.2,zorder=2,yoffset=0) # draw meridians

        plot_shapefiles(m,ax,faults=False)

        lon = staDb_df['LON'].values
        lat = staDb_df['LAT'].values
        #------------------------------------------ 
        if grid:
            nc = NetCDFFile(ocn_netcdf_path)
            data = nc['z'][:]*1000

            grid_lon = nc['lon'][:]
        #     grid_lon[grid_lon<0]+=360

            x_grid,y_grid = _np.meshgrid(grid_lon, nc['lat'][:])
            xx, yy = m(x_grid,y_grid)
            clevs=_np.arange(0,grid_max,0.25)
            cs = m.contourf(xx, yy, data,clevs,zorder=0,cmap=cmap,)
            cbar = m.colorbar(cs,location='left',shrink=0.2,fraction=0.046, pad=0.04)

        x,y = m(lon,lat)       
        
        if label_sites:

            staDb_df_not_zoomed = staDb_df
            x_no_zoom,y_no_zoom = m(staDb_df_not_zoomed['LON'].values,staDb_df_not_zoomed['LAT'].values)

            m.scatter(x_no_zoom,y_no_zoom,zorder=25,color='r',marker='+',s = 2,linewidth=0.5)
            for i in range(staDb_df_not_zoomed.shape[0]):
                if _np.isin(staDb_df_not_zoomed.iloc[i]['SITE'],stations_left):
                    ax.text(x_no_zoom[i]-45000,y_no_zoom[i]+0,staDb_df_not_zoomed.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=35)
                elif _np.isin(staDb_df_not_zoomed.iloc[i]['SITE'],stations_down):
                    ax.text(x_no_zoom[i]+8000,y_no_zoom[i]-8000,staDb_df_not_zoomed.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=35)
                else:
                    ax.text(x_no_zoom[i]+8000,y_no_zoom[i]+0,staDb_df_not_zoomed.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=35)
        if vectors:
            vecs = []        
            for i in range(staDb_df.shape[0]):
                for c in range(len(constellations)):
                    vecs.append( ax.arrow(x[i],y[i],
                                x_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                y_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                linewidth=0.1,width=arrow_width,head_width=50*arrow_width,
                                color=colors.loc[constellations[c]].color,label=constellations[c],length_includes_head=True,zorder=20))
                    if ellipses:
                        ax.add_patch(mpatches.Ellipse(
                            xy=[x[i]+x_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff, 
                               y[i]+y_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff],
                            width=semiAxisA[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                            height=semiAxisP[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                            angle=phase[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent] - 90,
                            fc=colors.loc[constellations[c]].color,
                            alpha = alpha_ellipse,
                            edgecolor=colors.loc[constellations[c]].color,zorder=20)) #X4 for 95% confidence
        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
        # adding a zoom plot :
        if stations_zoomed:

            staDb_df_zoomed = staDb_df[staDb_df['SITE'].isin(stations_zoomed)]
            # lon_zoomed = staDb_df_zoomed['LON'].values
            # lat_zoomed = staDb_df_zoomed['LAT'].values

            center_zoomed = get_center(staDb_df_zoomed,crnrs_coeff)
            height_zoomed = width_zoomed * proportion_zoomed
            llcrnrlat_zoomed,urcrnrlat_zoomed,llcrnrlon_zoomed,urcrnrlon_zoomed = gen_corners(center_lat=center_zoomed[1],center_lon=center_zoomed[0],height=height_zoomed,width=width_zoomed)
#             print(llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon)
            
#             return gen_corners(center_lat=center_zoomed[1],center_lon=center_zoomed[0],height=height_zoomed,width=width_zoomed)
            
#             crnrs_zoomed = get_crnrs(staDb_df_zoomed,crnrs_coeff)
            # x_zoom,y_zoom = m(lon_zoomed,lat_zoomed)
            from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
            from mpl_toolkits.axes_grid1.inset_locator import mark_inset
            

            axins = zoomed_inset_axes(ax, 2.5, loc='center',bbox_to_anchor=(700/100*dpi, 250/100*dpi, 0.5, 0.5)) # zoom = 4 borderpad=-4,
            if label_sites:
                m.scatter(x,y,ax=axins,zorder=10,color='r',marker='+',label='test')
                m.scatter(x,y,ax=ax,zorder=10,color='r',marker='+')
                
                for i in range(staDb_df.shape[0]):
                    axins.text(x[i],y[i],staDb_df.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=30)
#                     if _np.isin(staDb_df.iloc[i]['SITE'],stations_left):
#                         axins.text(x[i],y[i],staDb_df.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=15)
#                     elif _np.isin(staDb_df.iloc[i]['SITE'],stations_down):
#                         axins.text(x[i],y[i],staDb_df.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=15)
#                     else:
#                         axins.text(x[i],y[i],staDb_df.iloc[i]['SITE'],fontsize=fontsize,color = '0.10',zorder=15)

            m.fillcontinents(color='0.95',lake_color='0.75')
            m.drawcoastlines(linewidth=0.5,color='grey',ax=axins)

#             m.etopo(ax=axins)
            x1,y1 = m(llcrnrlon_zoomed.values,llcrnrlat_zoomed.values)
            x2,y2 = m(urcrnrlon_zoomed.values,urcrnrlat_zoomed.values)

            if vectors:
                vecs = []        
                for i in range(staDb_df.shape[0]):
                    for c in range(len(constellations)):
                        vecs.append( axins.arrow(x[i],y[i],
                                    x_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                    y_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                    width=arrow_width,head_width=35*arrow_width, color=colors.loc[constellations[c]].color,label=constellations[c],length_includes_head=True,zorder=20))
                        if ellipses:
                            axins.add_patch(mpatches.Ellipse(
                                xy=[x[i]+x_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff, 
                                   y[i]+y_otl[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff],
                                width=semiAxisA[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                height=semiAxisP[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent]*otl_res_coeff,
                                angle=phase[constellations[c],component].loc[staDb_df['SITE'].iloc[i],constituent] - 90,
                                fc=colors.loc[constellations[c]].color,
                                alpha = alpha_ellipse,
                                edgecolor=colors.loc[constellations[c]].color,zorder=20)) #X4 for 95% confidence
            
            asb_vec = AnchoredSizeBar(axins.transData,otl_res_coeff,r'{}  1$mm$'.format(names2labels(constituent).values[0] +' '+component.capitalize()),loc=2,pad=0.1, borderpad=0.25, sep=5, frameon=False)
            axins.add_artist(asb_vec)
           
            plot_shapefiles(m,axins)
            
            axins.set_xlim(x1,x2)
            axins.set_ylim(y1,y2)
            plt.xticks(visible=False)
            plt.yticks(visible=False)
            mark_inset(ax, axins, loc1=1, loc2=2, fc="none", ec='grey',linestyle='--')

#             asb = AnchoredSizeBar(axins.transData,30000.,"30 km",loc=1,pad=0.1, borderpad=0.25, sep=5, frameon=False)
#             axins.add_artist(asb)

            



            # Now adding the colorbar
        arrow = []; arrow_label = []
        if vectors:
            asb_main = AnchoredSizeBar(ax.transData, otl_res_coeff,r'{}  1$mm$'.format(names2labels(constituent).values[0] +' '+component.capitalize()),loc=2, pad=0.25, borderpad=0.5, sep=5, frameon=False,)
            ax.add_artist(asb_main)

            for i in range(len(constellations)):
                arrow.append(vecs[i])
                arrow_label.append(vecs[i].get_label())

            ax.legend(arrow, arrow_label,loc='upper right')
    #     fig.legend(vecs)
    #     if filename !=None:
    #         fig.savefig(filename+'.png', transparent=True,dpi=300)
#         if vectors:
#             return vecs[0]



b = ('''OBJECTID	Name	Lon	Lat
1	Hikurangi plateau	176.8798828	-41.23693848
2	Hikurangi plateau	176.2136841	-40.77215576
3	Hikurangi plateau	176.854126	-39.96490479
4	Hikurangi plateau	176.8233032	-39.39147949
5	Hikurangi plateau	177.151123	-39.01776123
6	Hikurangi plateau	177.6373291	-38.93585205
7	Hikurangi plateau	178.2286987	-38.34918213
8	Hikurangi plateau	179.0429077	-38.6060791
9	Hikurangi plateau	184.0784355	-27.7369072
10	Hikurangi plateau	198.3026299	-37.94797044
11	Hikurangi plateau	194.685861	-41.06800694
12	Hikurangi plateau	176.8798828	-41.23693848
13	Macman_regionSW	160.0070322	-33.33534868
14	Macman_regionSW	168.6331787	-44.08514404
15	Macman_regionSW	166.8084717	-46.01739502
16	Macman_regionSW	160.4858476	-53.87562152
17	Macman_regionSW	146.0860583	-46.17077226
18	Macman_regionSW	160.0070322	-33.33534868
19	North Taranaki Bight	174.2783813	-39.42193603
20	North Taranaki Bight	173.0637207	-38.55657959
21	North Taranaki Bight	172.4992065	-39.01824951
22	North Taranaki Bight	161.5836646	-31.73197396
23	North Taranaki Bight	164.7267058	-28.45137671
24	North Taranaki Bight	173.1566162	-34.590271
25	North Taranaki Bight	175.3453979	-37.43994141
26	North Taranaki Bight	174.2783813	-39.42193603
27	Challenger plateau	160.0070322	-33.33534868
28	Challenger plateau	161.5836646	-31.73197396
29	Challenger plateau	172.4992065	-39.01824951
30	Challenger plateau	171.2857056	-40.01086426
31	Challenger plateau	172.4178467	-40.79669189
32	Challenger plateau	171.6893921	-42.19567871
33	Challenger plateau	170.3637085	-43.2633667
34	Challenger plateau	168.6331787	-44.08514404
35	Challenger plateau	160.0070322	-33.33534868
36	Havre trough	179.0429077	-38.6060791
37	Havre trough	175.3453979	-37.43994141
38	Havre trough	180.3064376	-24.8387622
39	Havre trough	184.0784355	-27.7369072
40	Havre trough	179.0429077	-38.6060791
41	Cook strait	171.2857056	-40.01086426
42	Cook strait	173.0637207	-38.55657959
43	Cook strait	176.8798828	-41.23693848
44	Cook strait	175.1957397	-42.72546387
45	Cook strait	171.2857056	-40.01086426
46	Chatham rise	170.4800415	-45.6842041
47	Chatham rise	171.2632446	-44.31738281
48	Chatham rise	174.0753174	-41.94750977
49	Chatham rise	175.1957397	-42.72546387
50	Chatham rise	176.8798828	-41.23693848
51	Chatham rise	194.685861	-41.06800694
52	Chatham rise	187.4313665	-46.8959827
53	Chatham rise	170.4800415	-45.6842041
54	Campbell plateau	187.4313665	-46.8959827
55	Campbell plateau	171.4758981	-58.94149555
56	Campbell plateau	160.4858476	-53.87562152
57	Campbell plateau	166.8084717	-46.01739502
58	Campbell plateau	169.3103027	-46.52923584
59	Campbell plateau	170.4800415	-45.6842041
60	Campbell plateau	187.4313665	-46.8959827
61	Northland shelf	180.3158249	-24.84606452
62	Northland shelf	175.3453979	-37.43994141
63	Northland shelf	173.1566162	-34.590271
64	Northland shelf	164.7267058	-28.45137671
65	Northland shelf	172.9127901	-19.43155868
66	Northland shelf	180.3158249	-24.84606452
''')
def plot_polygons(ax,m,b=b,edgecolor='k',facecolor=None,alpha=0.4):
    series0 = _pd.Series(b).str.split('\n',expand=True).T.iloc[1:,0] #
    series1 = series0[series0!=''].str.split('\t',expand=True)
    series1[1]= series1[1].astype('category')
    series1[2]= series1[2].astype(float)
    series1[3]= series1[3].astype(float)
    series1.set_index(1,inplace=True)
    
    cmap = cm.tab20b
    # m.drawcoastlines(linewidth=0.5,color='grey',zorder=1)
    # m.fillcontinents(color='0.7',lake_color='0.5')
    # m.drawparallels(_np.arange(-70.,0,20.),labels=[1,0,0,0],color='black',dashes=[1,0],labelstyle='',linewidth=0.2,zorder=2) # draw parallels
    # m.drawmeridians(_np.arange(145.,200.,20.),labels=[0,1,1,0],color='black',dashes=[1,0],labelstyle='',linewidth=0.2,zorder=2,yoffset=0) # draw meridians

    patches = []
    for i in range(len(series1.index.categories)):
        poly = series1.index.categories[i]
        homeplate = _pd.DataFrame(m(series1.loc[poly][2].values,series1.loc[poly][3].values)).T.values
        patches.append(Polygon(homeplate))
        ax.add_collection(PatchCollection([Polygon(homeplate)],facecolor=cmap(1*i/10) if facecolor is None else facecolor, alpha=alpha,edgecolor=edgecolor, linewidths=0.8,zorder=20))