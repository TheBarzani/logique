import csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
with (r/'c5-admitted-plot-data.csv').open() as f:rows=list(csv.DictReader(f))
fig,axes=plt.subplots(1,2,figsize=(9,3.6),sharey=True)
for ax,regime in zip(axes,['R1','R2']):
 data=[d for d in rows if d['regime']==regime];j=[int(d['iterations']) for d in data]
 ax.plot(j,[float(d['analytical']) for d in data],color='black',linewidth=1,label='Analytical ideal prediction')
 ax.plot(j,[float(d['success']) for d in data],'o',fillstyle='none',label='Saved ideal circuit execution')
 ax.plot(j,[float(d['unused_code_probability']) for d in data],'s--',markersize=4,label='Unused-code probability')
 ax.set(title=regime+(' — binary support (1024)' if regime=='R1' else ' — valid-code support (243)'),xlabel='Grover iterations j',ylim=(-.03,1.03),xticks=j);ax.grid(alpha=.2)
axes[0].set_ylabel('Probability (dimensionless)');axes[1].legend(fontsize=7,loc='lower left')
fig.suptitle('C5, k=3: 30 proper colorings, complete predicate, 11-wire best-fit oracle',fontsize=10)
fig.tight_layout();fig.savefig(r/'c5-admitted-iterations.png',dpi=180);fig.savefig(r/'c5-admitted-iterations.pdf');plt.close(fig)
(r/'figure-manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [r/'c5-admitted-plot-data.csv',r/'plot_admitted_c5.py',r/'c5-admitted-iterations.png',r/'c5-admitted-iterations.pdf']},indent=2)+'\n')
print('Saved two panels from ten admitted rows; no simulations, shots or fitted data; independent presentation review pending')
