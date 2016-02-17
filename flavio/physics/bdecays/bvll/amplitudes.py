from flavio.physics.bdecays.common import lambda_K, beta_l
from math import sqrt, pi
from flavio.physics.bdecays.wilsoncoefficients import wctot_dict, get_wceff
from flavio.physics.running import running
from flavio.config import config
from flavio.physics.bdecays.common import lambda_K, beta_l, meson_quark, meson_ff
from flavio.physics.common import conjugate_par, conjugate_wc, add_dict
from flavio.physics.bdecays import matrixelements, angular
from flavio.physics import ckm
from flavio.physics.bdecays.bvll import qcdf
from flavio.classes import AuxiliaryQuantity

def prefactor(q2, par, B, V, lep):
    GF = par['Gmu']
    ml = par['m_'+lep]
    scale = config['renormalization scale']['bvll']
    alphaem = running.get_alpha(par, scale)['alpha_e']
    di_dj = meson_quark[(B,V)]
    xi_t = ckm.xi('t',di_dj)(par)
    if q2 <= 4*ml**2:
        return 0
    return 4*GF/sqrt(2)*xi_t*alphaem/(4*pi)

def get_ff(q2, par, B, V):
    ff_name = meson_ff[(B,V)] + ' form factor'
    return AuxiliaryQuantity.get_instance(ff_name).prediction(par_dict=par, wc_obj=None, q2=q2)


def helicity_amps_ff(q2, wc_obj, par_dict, B, V, lep, cp_conjugate):
    par = par_dict.copy()
    if cp_conjugate:
        par = conjugate_par(par)
    scale = config['renormalization scale']['bvll']
    label = meson_quark[(B,V)] + lep + lep # e.g. bsmumu, bdtautau
    wc = wctot_dict(wc_obj, label, scale, par)
    if cp_conjugate:
        wc = conjugate_wc(wc)
    wc_eff = get_wceff(q2, wc, par, B, V, lep, scale)
    ml = par['m_'+lep]
    mB = par['m_'+B]
    mV = par['m_'+V]
    mb = running.get_mb(par, scale)
    N = prefactor(q2, par, B, V, lep)
    ff = get_ff(q2, par, B, V)
    h = angular.helicity_amps_v(q2, mB, mV, mb, 0, ml, ml, ff, wc_eff, N)
    return h

# get spectator scattering contribution
def get_ss(q2, wc_obj, par_dict, B, V, lep, cp_conjugate):
    # this only needs to be done for low q2 - which doesn't exist for taus!
    if lep == 'tau' or q2 >= 9:
        return {('0' ,'V'): 0, ('0' ,'A'): 0,
                ('pl' ,'V'): 0, ('pl' ,'A'): 0,
                ('mi' ,'V'): 0, ('mi' ,'A'): 0, }
    ss_name = B+'->'+V+lep+lep + ' spectator scattering'
    return AuxiliaryQuantity.get_instance(ss_name).prediction(par_dict=par_dict, wc_obj=wc_obj, q2=q2, cp_conjugate=cp_conjugate)


def helicity_amps(q2, wc_obj, par, B, V, lep):
    return add_dict((
        helicity_amps_ff(q2, wc_obj, par, B, V, lep, cp_conjugate=False),
        get_ss(q2, wc_obj, par, B, V, lep, cp_conjugate=False)
        ))

def helicity_amps_bar(q2, wc_obj, par, B, V, lep):
    return add_dict((
        helicity_amps_ff(q2, wc_obj, par, B, V, lep, cp_conjugate=True),
        get_ss(q2, wc_obj, par, B, V, lep, cp_conjugate=True)
        ))
