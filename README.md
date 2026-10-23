# ArUco_soja — Medição de folhas de soja com marcador ArUco

Script de visão computacional que mede o **comprimento e a largura reais (em cm)** de uma folha de soja a partir de:

1. uma foto da folha com um **marcador ArUco** de tamanho conhecido ao lado;
2. a **máscara de segmentação** da folha gerada por um dos modelos do projeto (U-Net, DeepLabV3+, SAM etc.).

O marcador serve como régua: como seu tamanho real é conhecido, é possível converter pixels em centímetros.

## Como funciona

O fluxo está todo em [`train.py`](train.py) (apesar do nome, o script não treina modelo, ele faz a medição):

1. **Carregamento**: lê a imagem original (`aruco1.jpg`) e a máscara binária do modelo (`aruco1_OUT.png`).
2. **Calibração com ArUco**: detecta o marcador com o dicionário `DICT_4X4_50` do OpenCV, mede a largura do lado em pixels e calcula o fator de conversão `cm/pixel` (o marcador tem `TAMANHO_REAL_ARUCO_CM = 1.0` cm).
3. **Extração das medidas**: binariza a máscara, encontra o maior contorno (a folha) e ajusta um retângulo de área mínima (`cv2.minAreaRect`). O lado maior é o comprimento e o lado menor é a largura.
4. **Saída**: desenha o retângulo e as medidas na imagem, salva em `resultado_medicao.jpg` e mostra uma janela (Tkinter) com o resultado.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `train.py` | Script de calibração e medição |
| `aruco.jpg`, `aruco1.jpg`, `aruco-7.jpg` | Fotos de exemplo com o marcador ArUco |
| `aruco_OUT.png`, `aruco1_OUT.png`, `aruco-7_OUT.png` | Máscaras de segmentação correspondentes |
| `resultado_medicao.jpg` | Exemplo de saída com as medidas desenhadas |
| `Soja aruco/` | Fotos de folhas com marcador (não versionadas, ~158 MB) |

## Requisitos

- Python 3.8+
- `opencv-contrib-python` (módulo `cv2.aruco`, versão 4.7 ou superior por causa da API `ArucoDetector`)
- `numpy`
- `tkinter` (normalmente já vem com o Python; no Ubuntu: `sudo apt install python3-tk`)

```bash
pip install opencv-contrib-python numpy
```

## Uso

1. Coloque a foto e a máscara na pasta do projeto.
2. Ajuste os nomes em `train.py` (`imagem_original` e `mascara_modelo`) e, se necessário, o tamanho real do marcador em `TAMANHO_REAL_ARUCO_CM`.
3. Execute:

```bash
python train.py
```

A imagem anotada é salva como `resultado_medicao.jpg`.

## Observações

- A máscara deve ter o mesmo tamanho da foto original e a folha em branco (valores > 127).
- Apenas o primeiro marcador detectado é usado na calibração.
- A precisão depende de a folha e o marcador estarem no mesmo plano e da câmera estar o mais perpendicular possível.
