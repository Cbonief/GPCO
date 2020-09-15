# INFO

This folder contains info related to the Boost Half Bridge Converter and also the converter design by Carolina Knaesel (2018) in her work regarding the converter.

## Boost Half Bridge

##$ Lista dos parâmetros de Projeto
- Vo
- V ('Nominal', 'Max', 'Min')
- Po
- Bmax ('Transformer', 'EntranceInductor', 'AuxiliaryInductor')
- dIin_max
- dVo_max
- dVc1
- dVc2
- Jmax *(futuramente fará parte da classe Cable)*


### Lista de Parâmetros de Segurança
- Vc
- Vd
- Vs
- Ic
- Id
- Is
- ku (Transformer', 'EntranceInductor', 'AuxiliaryInductor')


### Lista de Variáveis (27 no Total: 3 Contínuas e 24 Discretas)
	
#### Contínuas
- fs
- Li (valor da indutância)
- Lk (valor da indutância)

#### Discretas
- C1, C2, C3, C4.
- S1 e S2.
- D3 e D4.
##### Transformador
- Núcleo
- Np e Ns.
- NcondP e NcondS.
- Cabo do Primário e do Secundário.
##### Li
- Núcleo.
- N
- Ncond
- Cabo
##### Lk
- Núcleo
- N
- Ncond
- Cabo


Lista de Restrições
