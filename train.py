import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import messagebox

# ====================================================================
# 1. CONFIGURAÇÃO DA INTERFACE (Tkinter)
# ====================================================================
# Oculta a janela base vazia do Tkinter, deixando apenas as caixas de aviso
root = tk.Tk()
root.withdraw()

# ====================================================================
# 2. CARREGAMENTO DAS IMAGENS 
# ====================================================================
imagem_original = cv2.imread('aruco1.jpg')
mascara_modelo = cv2.imread('aruco1_OUT.png', cv2.IMREAD_GRAYSCALE)

# Trava de segurança para a interface caso a imagem não exista
if imagem_original is None or mascara_modelo is None:
    messagebox.showerror("Erro de Leitura", "Não foi possível carregar as imagens. Verifique os caminhos.")
    exit()

# ====================================================================
# 3. CALIBRAÇÃO COM O MARCADOR ARUCO
# ====================================================================
TAMANHO_REAL_ARUCO_CM = 1.0 

dicionario_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parametros_aruco = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dicionario_aruco, parametros_aruco)

cantos, ids, rejeitados = detector.detectMarkers(imagem_original)

fator_conversao = None

if len(cantos) > 0:
    canto_aruco = cantos[0][0] 
    largura_aruco_pixels = math.dist(canto_aruco[0], canto_aruco[1])
    fator_conversao = TAMANHO_REAL_ARUCO_CM / largura_aruco_pixels
else:
    messagebox.showwarning("Aviso", "Marcador ArUco não encontrado na imagem original!")

# ====================================================================
# 4. EXTRAÇÃO DAS MEDIDAS DA FOLHA DE SOJA
# ====================================================================
if fator_conversao is not None:
    _, mascara_binaria = cv2.threshold(mascara_modelo, 127, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(mascara_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contornos:
        contorno_folha = max(contornos, key=cv2.contourArea)
        retangulo = cv2.minAreaRect(contorno_folha)
        
        (centro_x, centro_y), (dimensao_1_px, dimensao_2_px), angulo = retangulo
        
        comprimento_px = max(dimensao_1_px, dimensao_2_px)
        largura_px = min(dimensao_1_px, dimensao_2_px)
        
        comprimento_cm = comprimento_px * fator_conversao
        largura_cm = largura_px * fator_conversao
        
        # Desenha o retângulo verde
        box = cv2.boxPoints(retangulo)
        box = np.int32(box) 
        cv2.drawContours(imagem_original, [box], 0, (0, 255, 0), 6)
        
        # Escreve as medidas na própria imagem
        texto_medida = f"C: {comprimento_cm:.2f}cm | L: {largura_cm:.2f}cm"
        cv2.putText(imagem_original, texto_medida, (int(centro_x) - 100, int(centro_y)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 255), 2, cv2.LINE_AA)
        
        # ---------------------------------------------------------
        # A SOLUÇÃO: Salva a imagem no disco em vez de tentar abrir
        # ---------------------------------------------------------
        nome_arquivo_saida = 'resultado_medicao.jpg'
        cv2.imwrite(nome_arquivo_saida, imagem_original)
        
        # Abre a Interface Pop-up (GUI) com os resultados formatados
        mensagem = (f"Análise concluída com sucesso!\n\n"
                    f"Comprimento: {comprimento_cm:.2f} cm\n"
                    f"Largura:     {largura_cm:.2f} cm\n\n"
                    f"A imagem com o desenho foi salva na sua pasta como '{nome_arquivo_saida}'.")
        
        messagebox.showinfo("Resultados da Medição", mensagem)
        
    else:
        messagebox.showerror("Erro de Segmentação", "Nenhum contorno de folha encontrado na máscara!")
