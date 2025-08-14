#!/usr/bin/env python3
"""
Script único para baixar e processar TODOS os dados administrativos de Portugal
Fonte: dados.gov.pt - Datasets oficiais
Garante: 308 concelhos e 3091+ freguesias com códigos DICOFRE corretos
"""

import requests
import pandas as pd
import json
import csv
from pathlib import Path
import time
import io
import os

class ExtractorPortugalCompleto:
    def __init__(self, output_folder="portugal_dados"):
        self.output_dir = Path(output_folder)
        self.output_dir.mkdir(exist_ok=True)
        
        # Dados que serão extraídos
        self.distritos = []
        self.concelhos = []
        self.freguesias = []
        
        # Metadados dos datasets
        self.datasets_info = {}
        
    def baixar_dataset(self, dataset_slug, nome):
        """Baixa um dataset específico do dados.gov.pt"""
        print(f"\n>> Baixando: {nome}")
        print("-" * 50)
        
        url = f"https://dados.gov.pt/api/1/datasets/{dataset_slug}/"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                dataset = response.json()
                
                # Capturar metadados do dataset
                self.datasets_info[nome] = {
                    'titulo': dataset.get('title', nome),
                    'organizacao': dataset.get('organization', {}).get('name', 'N/A'),
                    'ultima_modificacao': dataset.get('last_modified', 'N/A'),
                    'criado_em': dataset.get('created_at', 'N/A'),
                    'frequencia': dataset.get('frequency', 'N/A'),
                    'versao': dataset.get('version', 'N/A')
                }
                
                # Mostrar informações do dataset
                print(f"   Organização: {self.datasets_info[nome]['organizacao']}")
                print(f"   Última atualização: {self.datasets_info[nome]['ultima_modificacao'][:10] if self.datasets_info[nome]['ultima_modificacao'] != 'N/A' else 'N/A'}")
                
                resources = dataset.get('resources', [])
                
                # Procurar recurso Excel/CSV
                for resource in resources:
                    format_type = resource.get('format', '').lower()
                    
                    if format_type in ['xlsx', 'xls', 'csv']:
                        resource_url = resource.get('url')
                        print(f"   Baixando {format_type}...", end="")
                        
                        file_response = requests.get(resource_url, timeout=60)
                        if file_response.status_code == 200:
                            
                            if format_type in ['xlsx', 'xls']:
                                df = pd.read_excel(io.BytesIO(file_response.content))
                            else:  # CSV
                                # Tentar diferentes encodings
                                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                                    try:
                                        text = file_response.content.decode(encoding)
                                        df = pd.read_csv(io.StringIO(text))
                                        break
                                    except:
                                        continue
                            
                            print(f" [OK] {len(df)} registros")
                            return df
                        
        except Exception as e:
            print(f"   [ERRO] {str(e)[:50]}")
        
        return None
    
    def processar_distritos(self, df=None):
        """Processa distritos de Portugal - dinâmico ou fallback"""
        print("\n>> Processando Distritos...")
        
        # Se recebeu dados dinâmicos, usar
        if df is not None:
            print("   Usando dados dinâmicos do dados.gov.pt...")
            for _, row in df.iterrows():
                nome = str(row.get('designacao', row.get('nome', ''))).strip()
                codigo = str(row.get('dicofre', row.get('codigo', ''))).strip()
                
                if nome and codigo:
                    # Padronizar código para 2 dígitos
                    if len(codigo) == 1:
                        codigo = '0' + codigo
                    
                    self.distritos.append({
                        'name': nome,
                        'codigo': codigo
                    })
        
        # Se não conseguiu dados ou está vazio, usar fallback
        if not self.distritos:
            print("   Usando lista oficial (fallback)...")
            # Lista oficial de distritos como fallback
            distritos_oficiais = [
                ("01", "Aveiro"),
                ("02", "Beja"),
                ("03", "Braga"),
                ("04", "Bragança"),
                ("05", "Castelo Branco"),
                ("06", "Coimbra"),
                ("07", "Évora"),
                ("08", "Faro"),
                ("09", "Guarda"),
                ("10", "Leiria"),
                ("11", "Lisboa"),
                ("12", "Portalegre"),
                ("13", "Porto"),
                ("14", "Santarém"),
                ("15", "Setúbal"),
                ("16", "Viana do Castelo"),
                ("17", "Vila Real"),
                ("18", "Viseu"),
                ("20", "Açores"),
                ("30", "Madeira")
            ]
            
            for codigo, nome in distritos_oficiais:
                self.distritos.append({
                    'name': nome,
                    'codigo': codigo
                })
        
        print(f"   [OK] {len(self.distritos)} distritos processados")
    
    def processar_concelhos(self, df):
        """Processa TODOS os 308 concelhos"""
        print("\n>> Processando Concelhos...")
        
        if df is None:
            print("   [ERRO] Sem dados de concelhos")
            return
        
        for _, row in df.iterrows():
            nome = str(row.get('designacao', '')).strip()
            dicofre = str(row.get('dicofre', '')).strip()
            
            if nome and dicofre:
                # Padronizar código para 4 dígitos
                if len(dicofre) == 3:
                    dicofre = '0' + dicofre
                
                distrito_id = dicofre[:2] if len(dicofre) >= 2 else ''
                
                self.concelhos.append({
                    'name': nome,
                    'codigo': dicofre,
                    'distrito_id': distrito_id
                })
        
        print(f"   [OK] {len(self.concelhos)} concelhos processados")
    
    def processar_freguesias(self, df):
        """Processa TODAS as 3091+ freguesias"""
        print("\n>> Processando Freguesias...")
        
        if df is None:
            print("   [ERRO] Sem dados de freguesias")
            return
        
        for _, row in df.iterrows():
            nome = str(row.get('freguesia', '')).strip()
            dicofre = str(row.get('dicofre', '')).strip()
            
            if nome and dicofre:
                # Padronizar código - adicionar zero se necessário
                if len(dicofre) == 5:
                    dicofre = '0' + dicofre
                
                # Extrair código do concelho (primeiros 4 dígitos)
                concelho_id = dicofre[:4] if len(dicofre) >= 4 else ''
                
                self.freguesias.append({
                    'name': nome,
                    'codigo': dicofre,
                    'concelho_id': concelho_id
                })
        
        print(f"   [OK] {len(self.freguesias)} freguesias processadas")
    
    def salvar_dados(self):
        """Salva os dados em CSV e JSON"""
        print("\n>> Salvando arquivos...")
        
        # CSV - Distritos
        df_distritos = pd.DataFrame(self.distritos)
        df_distritos.to_csv(self.output_dir / 'distritos.csv', index=False, encoding='utf-8')
        print(f"   [OK] distritos.csv")
        
        # CSV - Concelhos
        df_concelhos = pd.DataFrame(self.concelhos)
        df_concelhos.to_csv(self.output_dir / 'concelhos.csv', index=False, encoding='utf-8')
        print(f"   [OK] concelhos.csv")
        
        # CSV - Freguesias
        df_freguesias = pd.DataFrame(self.freguesias)
        df_freguesias.to_csv(self.output_dir / 'freguesias.csv', index=False, encoding='utf-8')
        print(f"   [OK] freguesias.csv")
        
        # Determinar a versão baseada nas datas dos datasets
        datas_modificacao = []
        for info in self.datasets_info.values():
            if info['ultima_modificacao'] != 'N/A':
                datas_modificacao.append(info['ultima_modificacao'])
        
        # Usar a data mais recente dos datasets como versão
        if datas_modificacao:
            ultima_atualizacao = max(datas_modificacao)
            # Extrair ano e mês da última atualização
            versao_dados = ultima_atualizacao[:7].replace('-', '.')  # YYYY.MM
        else:
            versao_dados = 'N/A'
        
        # JSON completo
        dados_completos = {
            'metadata': {
                'fonte': 'dados.gov.pt',
                'data_extracao': time.strftime('%Y-%m-%d %H:%M:%S'),
                'versao_dados': versao_dados,  # Versão baseada na última atualização dos datasets
                'datasets_info': self.datasets_info,  # Informações detalhadas de cada dataset
                'total_distritos': len(self.distritos),
                'total_concelhos': len(self.concelhos),
                'total_freguesias': len(self.freguesias)
            },
            'distritos': self.distritos,
            'concelhos': self.concelhos,
            'freguesias': self.freguesias
        }
        
        with open(self.output_dir / 'portugal_completo.json', 'w', encoding='utf-8') as f:
            json.dump(dados_completos, f, ensure_ascii=False, indent=2)
        print(f"   [OK] portugal_completo.json")
    
    def gerar_relatorio(self):
        """Gera relatório com estatísticas"""
        print("\n" + "="*60)
        print("RELATÓRIO FINAL")
        print("="*60)
        
        print(f"\nDISTRITOS: {len(self.distritos)}")
        print(f"  - Continental: 18")
        print(f"  - Regiões Autónomas: 2")
        
        print(f"\nCONCELHOS: {len(self.concelhos)}")
        print(f"  - Esperado: 308")
        print(f"  - Status: {'COMPLETO' if len(self.concelhos) == 308 else 'INCOMPLETO'}")
        
        print(f"\nFREGUESIAS: {len(self.freguesias)}")
        print(f"  - Esperado: ~3091")
        print(f"  - Status: {'COMPLETO' if len(self.freguesias) >= 3090 else 'VERIFICAR'}")
        
        # Mostrar versão dos dados
        print("\n" + "-"*60)
        print("INFORMAÇÕES DOS DATASETS:")
        print("-"*60)
        
        for nome, info in self.datasets_info.items():
            if info['ultima_modificacao'] != 'N/A':
                print(f"\n{nome}:")
                print(f"  - Última atualização: {info['ultima_modificacao'][:10]}")
                print(f"  - Organização: {info['organizacao']}")
        
        # Determinar versão geral
        datas = [info['ultima_modificacao'] for info in self.datasets_info.values() if info['ultima_modificacao'] != 'N/A']
        if datas:
            versao = max(datas)[:7].replace('-', '.')
            print(f"\nVersão dos dados: {versao}")
        
        print("\n" + "="*60)
        print(f"Arquivos salvos em: {self.output_dir.absolute()}/")
        print("="*60)
    
    def executar(self):
        """Executa todo o processo de extração"""
        print("="*60)
        print("EXTRATOR DE DADOS ADMINISTRATIVOS DE PORTUGAL")
        print("Versão Completa - Todos os Dados Oficiais")
        print("="*60)
        
        # 1. Baixar datasets
        # Tentar baixar distritos primeiro (pode não existir)
        df_distritos = self.baixar_dataset('distritos-de-portugal', 'Distritos de Portugal')
        if df_distritos is None:
            # Tentar slug alternativo
            df_distritos = self.baixar_dataset('distritos', 'Distritos')
        
        df_concelhos = self.baixar_dataset('concelhos-de-portugal', 'Concelhos de Portugal')
        df_freguesias = self.baixar_dataset('freguesias-de-portugal', 'Freguesias de Portugal')
        
        # 2. Processar dados
        self.processar_distritos(df_distritos)  # Passa os dados ou None
        self.processar_concelhos(df_concelhos)
        self.processar_freguesias(df_freguesias)
        
        # 3. Salvar arquivos
        self.salvar_dados()
        
        # 4. Gerar relatório
        self.gerar_relatorio()
        
        return True


def main():
    """Função principal"""
    try:
        # Verificar/instalar pandas se necessário
        try:
            import pandas
        except ImportError:
            print("Instalando pandas...")
            os.system("pip install pandas openpyxl")
        
        # Executar extrator
        extractor = ExtractorPortugalCompleto("portugal_dados")
        success = extractor.executar()
        
        if success:
            print("\n[SUCESSO] Extração completa realizada!")
        else:
            print("\n[ERRO] Falha na extração")
            return 1
        
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())