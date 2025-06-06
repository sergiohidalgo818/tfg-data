
# RTXI circuits data

Here is contained all the different circuits that where recorded and connected with *RTXI*. The plugins used are the ported version of [rthybrid-for-rtxi](https://github.com/GNB-UAM/rthybrid-for-rtxi) to *RTXI V3*, they can be found [here](https://github.com/sergiohidalgo818/rthybrid-for-rtxi/tree/rthybrid-for-rtxi3/rtxi3).

## Virtual Hindmarsh-Rose in bidirectional synapse with electronic Hindmarsh-Rose

- Name of directory: `v_hr-e_hr`

### Plugin Parameters

**Control Panel:** 
  - Frequecy/Period: $10KHz$/$100\mu s$
  - Analog Scale: $250 \mu V/V$

**RTHybrid Hindmarsh-Rose model V2:**
  - Burst duration (s): 1
  - I: 3
  - a: 1
  - b: 3
  - c: 1
  - d: 5
  - r: 0.0021
  - s: 4
  - xr: -1.6
  - Vh: 1.07
  - x0: -0.712841
  - y0: -1.93688
  - z0: 3.16568


**RTHybrid Electrical Synapse 1:**
  - Phase g: 0.09
  - Antiphase g: -0.07

**RTHybrid Electrical Synapse 2:**
  - Phase g: 0.09
  - Antiphase g: -0.07

### Plugin Connection

Virtual is the RTHybrid model plugin and electrical is the physical electrical model.

```mermaid
---
config:
  theme: mc
  look: classic
  layout: dagre
---
flowchart TD
    n1(["RTHybrid Hindmarsh-Rose model V2"]) -- "Post-Synaptic Voltage" --> A(["Electrical Synapse Electrical-Virtual"])
    n2(["DAQ (Electrical Model)<br>"]) -- "Pre-Synaptic Voltage" --> A
    A -- Synaptic Current --> n1
    n2 -- "Post-Synaptic Voltage" --> n3(["Electrical Synapse Virtual-Electrical"])
    n1 -- "Pre-Synaptic Voltage" --> n3
    n3 -- "<span style=padding-left:>Synaptic Current</span>" --> n2
```

---

## Virtual Hindmarsh-Rose in bidirectional synapse with electronic Hindmarsh-Rose forwarded in DAQ

- Name of directory: `v_hr-e_hr-daq_forwarding`


**Control Panel:** 
  - Frequecy/Period: $10KHz$/$100\mu s$
  - Analog Scale: $250 \mu V/V$

**RTHybrid Hindmarsh-Rose model V2:**
  - Burst duration (s): 0.9
  - I: 3
  - a: 1
  - b: 3.02
  - c: 1
  - d: 5
  - r: 0.0099
  - s: 4
  - xr: -1.78
  - Vh: 1
  - x0: -0.712841
  - y0: -1.93688
  - z0: 3.16568


**RTHybrid Electrical Synapse 1:**
  - Phase g: 1.2
  - Antiphase g: -0.5

**RTHybrid Electrical Synapse 2:**
  - Phase g: 0.12
  - Antiphase g: -0.04

### Plugin Connection

Virtual is the RTHybrid model plugin and electrical is the physical electrical model.

```mermaid
---
config:
  theme: mc
  look: classic
  layout: dagre
---
flowchart TD
    n1(["RTHybrid Hindmarsh-Rose model V2"]) -- <br> --> n4(["DAQ (Virtual Forwarder)<br>"])
    n2(["DAQ (Electrical Model)<br>"]) -- "Pre-Synaptic Voltage" --> A(["Electrical Synapse Electrical-Virtual"])
    A -- Synaptic Current --> n1
    n2 -- "Post-Synaptic Voltage" --> n3(["Electrical Synapse Virtual-Electrical"])
    n1 -- "Pre-Synaptic Voltage" --> n3
    n3 -- "<span style=padding-left:>Synaptic Current</span>" --> n2
    n4 -- "Post-Synaptic Voltage" --> A
```


---

## Virtual Hindmarsh-Rose in monodirectional synapse with LP cell recording

- Name of directory: `v_hr-r_lp`


**Control Panel:** 
  - Frequecy/Period: $10KHz$/$100\mu s$


**RTHybrid Hindmarsh-Rose model V2:**
  - Burst duration (s): 1
  - I: 3
  - a: 1
  - b: 3
  - c: 1
  - d: 5
  - r: 0.00479
  - s: 4
  - xr: -1.6
  - Vh: 1
  - x0: -0.712841
  - y0: -1.93688
  - z0: 3.16568


**RTHybrid Electrical Synapse:**
  - Phase g: 0.35
  - Antiphase g: -0.55

### Plugin Connection

Virtual is the RTHybrid model plugin and electrical is the physical electrical model.

```mermaid
---
config:
  theme: mc
  look: classic
  layout: dagre
---
flowchart TD
    n1(["RTHybrid Hindmarsh-Rose model V2"]) -- "Post-Synaptic Voltage" --> A(["Electrical Synapse Recorded-Virtual"])
    n2(["DAQ (Living Neuron Recording)<br>"]) -- "Pre-Synaptic Voltage" --> A
    A -- Synaptic Current --> n1
    n5(["RTHybrid Amplitude Scale Offset"]) -- Scale and Offset --> A
    n3(["RTHybrid Burst analysis 1<br>"]) -- Min and Max --> n5
    n4(["RTHybrid Burst analysis 2"]) -- "<span style=color:>Min and Max</span>" --> n5
    n2 --> n3
    n1 --> n4
```
