# Momentos de Inércia (modular)
## Rodar o exemplo 3.1
No terminal, a partir da pasta onde está este pacote:

```bash
python -m momentos_inercia_v4.exemplos.exercicio_3_1
```

## Rodar a CLI
```bash
python -m momentos_inercia_v4.main
```

## Uso como biblioteca
```python
from momentos_inercia_v4 import SecaoComposta, Retangulo

secao = SecaoComposta(unidade_comprimento="cm")
secao.adicionar(Retangulo(base=10, altura=2, x=0, y=0))
r = secao.calcular(modo="quiet")
print(secao.resumo(r))
```

## Modos
- `modo="verbose"`: imprime passo a passo (didático)
- `modo="quiet"`: não imprime, só retorna resultados
