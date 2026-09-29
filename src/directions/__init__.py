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
from directions.j_signal import Signal
from directions.k_reticule import Reticule
from directions.l_tranche import Tranche
from directions.m_sceau import Sceau
from directions.n_autographe import Autographe
from directions.o_touche import Touche

ALL = [Point(), Pixel(), Incrust(), Horizon(), Maison(), Bulle(),
       Vitesse(), Protocole(), Terrain(), Signal(), Reticule(), Tranche(),
       Sceau(), Autographe(), Touche()]
BY_CODE = {d.code: d for d in ALL}
