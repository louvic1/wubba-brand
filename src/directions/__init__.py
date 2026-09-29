"""Registre des directions d'identité. L'ordre ici est l'ordre du catalogue."""
from directions.a_point import Point
from directions.b_pixel import Pixel
from directions.c_incrust import Incrust
from directions.d_horizon import Horizon
from directions.e_maison import Maison
from directions.f_bulle import Bulle
from directions.g_vitesse import Vitesse
from directions.h_protocole import Protocole
from directions.i_terrain import Terrain
from directions.j_lien import Lien
from directions.k_reticule import Reticule
from directions.l_tranche import Tranche

ALL = [Point(), Pixel(), Incrust(), Horizon(), Maison(), Bulle(),
       Vitesse(), Protocole(), Terrain(), Lien(), Reticule(), Tranche()]
BY_CODE = {d.code: d for d in ALL}
