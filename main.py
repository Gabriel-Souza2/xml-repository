from playwright.sync_api import sync_playwright, Playwright, Page, TimeoutError
import time

import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

import os
import sys
def classificar_imovel(titulo):
    # Definir a tabela de correspondências
    tabela = [
        {"Filtro VivaReal": "Apartamento", "Filtro Zap Imóveis": "Apartamento", "VRSync": "Residential / Apartment"},
        {"Filtro VivaReal": "Casa", "Filtro Zap Imóveis": "Casa", "VRSync": "Residential / Home"},
        {"Filtro VivaReal": "Casa de Condomínio", "Filtro Zap Imóveis": "Casa de Condomínio", "VRSync": "Residential / Condo"},
        {"Filtro VivaReal": "-", "Filtro Zap Imóveis": "Casa de Vila", "VRSync": "Residential / Village House"},
        {"Filtro VivaReal": "Chácara", "Filtro Zap Imóveis": "-", "VRSync": "Residential / Farm Ranch"},
        {"Filtro VivaReal": "Cobertura", "Filtro Zap Imóveis": "Cobertura", "VRSync": "Residential / Penthouse"},
        {"Filtro VivaReal": "Consultório", "Filtro Zap Imóveis": "-", "VRSync": "Commercial / Consultorio"},
        {"Filtro VivaReal": "Edifício Residencial", "Filtro Zap Imóveis": "-", "VRSync": "Commercial / Edificio Residencial"},
        {"Filtro VivaReal": "Fazenda/Sítios/Chácaras", "Filtro Zap Imóveis": "Fazenda / Sítio / Chácara", "VRSync": "Residential / Agricultural"},
        {"Filtro VivaReal": "Flat", "Filtro Zap Imóveis": "Flat", "VRSync": "Residential / Flat"},
        {"Filtro VivaReal": "Galpão/Depósito/Armazém", "Filtro Zap Imóveis": "Galpão / Depósito / Armazém", "VRSync": "Commercial / Industrial"},
        {"Filtro VivaReal": "-", "Filtro Zap Imóveis": "Garagem", "VRSync": "Commercial / Garage"},
        {"Filtro VivaReal": "Hotel/Motel/Pousada", "Filtro Zap Imóveis": "Hotel / Motel / Pousada", "VRSync": "Commercial / Hotel"},
        {"Filtro VivaReal": "Imóvel Comercial", "Filtro Zap Imóveis": "-", "VRSync": "Commercial / Building"},
        {"Filtro VivaReal": "Kitnet/Conjugado", "Filtro Zap Imóveis": "Kitnet", "VRSync": "Residential / Kitnet"},
        {"Filtro VivaReal": "Apartamento", "Filtro Zap Imóveis": "Studio", "VRSync": "Residential / Studio"},
        {"Filtro VivaReal": "-", "Filtro Zap Imóveis": "Andar / Laje Corporativa", "VRSync": "Commercial / Corporate Floor"},
        {"Filtro VivaReal": "Lote/Terreno", "Filtro Zap Imóveis": "Terreno / Lote / Condomínio", "VRSync": "Residential / Land Lot"},
        {"Filtro VivaReal": "Lote/Terreno", "Filtro Zap Imóveis": "Terreno / Lote / Condomínio", "VRSync": "Commercial / Land Lot"},
        {"Filtro VivaReal": "Ponto Comercial/Loja/Box", "Filtro Zap Imóveis": "Loja / Salão / Ponto Comercial", "VRSync": "Commercial / Business"},
        {"Filtro VivaReal": "Prédio/Edifício Inteiro", "Filtro Zap Imóveis": "Prédio Inteiro", "VRSync": "Commercial / Edificio Comercial"},
        {"Filtro VivaReal": "Sala/Conjunto", "Filtro Zap Imóveis": "Conjunto Comercial / Sala", "VRSync": "Commercial / Office"},
        {"Filtro VivaReal": "Sobrado", "Filtro Zap Imóveis": "-", "VRSync": "Residential / Sobrado"},
    ]

    # Normalizar o título para facilitar a busca (opcional)
    titulo = titulo.lower()

    if "estúdio" in titulo:
        return "Residential / Studio"
    
    if "terreno" in titulo:
        return "Residential / Land Lot"

    # Verificar correspondências na tabela
    for item in tabela:
        if item["Filtro VivaReal"].lower() in titulo or item["Filtro Zap Imóveis"].lower() in titulo:
            return item["VRSync"]

    # Retorno padrão caso nenhum filtro seja encontrado
    return "Residential / Home"

def create_listing_xml(data):
    print('Gerando XML...')
    print('Numero de imoveis capturados: ', len(data['listings']))
    # Criação do elemento raiz
    root = ET.Element("ListingDataFeed", attrib={
        "xmlns": "http://www.vivareal.com/schemas/1.0/VRSync",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://www.vivareal.com/schemas/1.0/VRSync http://xml.vivareal.com/vrsync.xsd",
    })

    # Cabeçalho
    header = ET.SubElement(root, "Header")
    ET.SubElement(header, "Provider").text = data["provider"]
    ET.SubElement(header, "Email").text = data["email"]
    ET.SubElement(header, "ContactName").text = data["contact_name"]
    ET.SubElement(header, "PublishDate").text = datetime.datetime.now().isoformat()
    ET.SubElement(header, "Telephone").text = data["telephone"]

    # Listagens
    listings = ET.SubElement(root, "Listings")
    for listing in data["listings"]:
        listing_element = ET.SubElement(listings, "Listing")
        ET.SubElement(listing_element, "ListingID").text = listing["id"]
        ET.SubElement(listing_element, "Title").text = listing["title"]
        ET.SubElement(listing_element, "TransactionType").text = listing["transaction_type"]
        ET.SubElement(listing_element, "PublicationType").text = listing["publication_type"]
        ET.SubElement(listing_element, "DetailViewUrl").text = listing["detail_view_url"]

        # Mídias
        media = ET.SubElement(listing_element, "Media")
        for item in listing["media"]:
            media_item = ET.SubElement(media, "Item", attrib={
                "medium": item["medium"],
                "caption": item.get("caption", ""),
                "primary": str(item.get("primary", False)).lower(),
            })
            media_item.text = item["url"]
        
        if listing['video']:
            ET.SubElement(media, "Item", attrib={"medium": "video"}).text = listing['video']

        # Detalhes
        details = ET.SubElement(listing_element, "Details")
        ET.SubElement(details, "PropertyType").text = listing["details"]["property_type"]
        ET.SubElement(details, "ListPrice", attrib={"currency": "BRL"}).text = str(listing["details"]["price"])

        if "PropertyAdministrationFee" in listing["details"]:
            ET.SubElement(details, "PropertyAdministrationFee", attrib={"currency": "BRL"}).text = str(listing["details"]["PropertyAdministrationFee"])

        if "YearlyTax" in listing["details"]:
            ET.SubElement(details, "Iptu", attrib={"currency": "BRL"}).text = str(listing["details"]["YearlyTax"])

        if "LotArea" in listing["details"]:
            ET.SubElement(details, "LotArea", attrib={"unit": "square metres"}).text = str(listing["details"]["LotArea"])

        if "LivingArea" in listing["details"]:
            ET.SubElement(details, "LivingArea", attrib={"unit": "square metres"}).text = str(listing["details"]["LivingArea"])

        if "Bathrooms" in listing["details"]:
            ET.SubElement(details, "Bathrooms").text = str(listing["details"]["Bathrooms"])

        if "Bedrooms" in listing["details"]:
            ET.SubElement(details, "Bedrooms").text = str(listing["details"]["Bedrooms"])

        if "Garage" in listing["details"]:
            ET.SubElement(details, "Garage").text = str(listing["details"]["Garage"])

        if "Description" in listing["details"]:
            ET.SubElement(details, "Description").text = str(listing["details"]["Description"])

        # Localização
        location = ET.SubElement(listing_element, "Location", attrib={"displayAddress": "Street"})
        ET.SubElement(location, "Country", attrib={"abbreviation": "BR"}).text = "Brasil"
        ET.SubElement(location, "State", attrib={"abbreviation": listing["location"]["state"]}).text = listing["location"]["state_name"]
        ET.SubElement(location, "City").text = listing["location"]["city"]
        ET.SubElement(location, "Neighborhood").text = listing["location"]["neighborhood"]
        ET.SubElement(location, "Address").text = listing["location"]["address"]
        ET.SubElement(location, "StreetNumber").text = listing["location"]["street_number"]

        contact = ET.SubElement(listing_element, "ContactInfo")
        ET.SubElement(contact, "Name").text = "Corretor Hélder"
        ET.SubElement(contact, "Telephone").text = "(48) 996797082"
        ET.SubElement(contact, "Website").text = "https://corretorhelder.com.br"
        ET.SubElement(contact, "Email").text = "helderresendebroker@gmail.com"
        
    # Gerar XML com formatação
    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open("output.xml", "w", encoding="utf-8") as file:
        file.write(xml_string)


def tratar_endereco(endereco):
    # Divida o endereço em partes
    partes = endereco.split(", ")    
    bairro = partes[-1].split(" - ")[0]


    return {
        "state": "SC",
        "state_name": "Santa Catarina",
        "city": "Florianópolis",
        "neighborhood": bairro,
        "address": partes[0],
        "street_number": partes[1],
    }

def estado_nome(sigla):
    # Mapeamento de siglas para nomes de estados (adapte conforme necessário)
    estados = {
        "SC": "Santa Catarina",
        "SP": "São Paulo",
        "RJ": "Rio de Janeiro",
        # Adicione outros estados conforme necessário
    }
    return estados.get(sigla, "Desconhecido")


def converter_valor(valor):
    """Converte string monetária para inteiro (em centavos, removendo caracteres não numéricos)."""
    return int("".join(filter(str.isdigit, valor)))


def run(playwright: Playwright, link):
    chromium = playwright.chromium  # ou "firefox" ou "webkit"
    browser = chromium.launch(headless=False)
    context = browser.new_context()  # Cria um novo contexto de navegador
    page = context.new_page()  # Página principal
    page.goto(link)

    # Lista para armazenar os itens extraídos
    all_items = set()

    # Selecionar a div que contém os resultados
    scroll_container_selector = '.col-xs-12.clb-search-result-property'

    # Obter altura inicial da div
    previous_height = page.locator(scroll_container_selector).evaluate("el => el.scrollHeight")

    visited_links = set()  # Para armazenar os links já visitados

    while True:
        # Rolar para o final da div
        page.locator(scroll_container_selector).evaluate("el => el.scrollTo(0, el.scrollHeight)")

        # Aguardar carregamento de novos itens
        page.wait_for_timeout(2000)  # Ajuste o tempo conforme necessário

        # Obter todos os links dentro de imovel-box-single
        links = page.locator('div.imovel-box-single a').evaluate_all(
            "nodes => nodes.map(node => node.href)"
        )

        # Adicionar links não visitados à lista
        new_links = [link for link in links if link not in visited_links]
        visited_links.update(new_links)

        # Verificar se a altura da div mudou
        current_height = page.locator(scroll_container_selector).evaluate("el => el.scrollHeight")
        if current_height == previous_height:
            print("Nenhum novo item carregado. Parando o scroll.")
            break

        previous_height = current_height

    listings = []

    # Visitar cada link coletado
    for link in visited_links:
        page.set_default_timeout(1000)

        details = {}

        try:
            print(f"Acessando link: {link}")
            page.goto(link, timeout=15000)
        except Exception as e:
            print('Erro ao acessar o link, continuando!')
            continue

        codigo = page.text_content("div.property-amenities > div:nth-child(1) > span")

        print(codigo)

        codigo = codigo.upper()

        codigo_extraido = codigo.replace("CÓDIGO: ", "").strip()

        titulo = page.text_content("div.clb-imovel-title h1")

        details['property_type'] = classificar_imovel(titulo)

        video_element = page.locator('a.modal-video-trigger[data-linkvideo]')

        video_url = None
        # Verifica se o elemento existe
        if video_element.is_visible():
            # Pega o valor do atributo 'data-linkvideo'
            video_id = video_element.get_attribute('data-linkvideo')
            
            if video_id:
                print("ID do vídeo:", video_id)
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print("URL do vídeo:", video_url)
            else:
                print("Atributo data-linkvideo não encontrado.")
        else:
            print("Elemento de vídeo não encontrado.")



        iframe_element = page.locator('iframe.embed-responsive-item')

        # Verifica se o elemento existe
        if iframe_element.is_visible():
            # Pega o valor do atributo 'src'
            iframe_src = iframe_element.get_attribute('src')
            
            if iframe_src:
                # Extrai a URL do vídeo do src do iframe
                video_url = iframe_src.split('?')[0]  # Remove qualquer parâmetro de consulta
                print("URL do vídeo:", video_url)
            else:
                print("Atributo 'src' não encontrado no iframe.")
        else:
            print("Iframe de vídeo não encontrado.")


        srcs_das_imagens = page.eval_on_selector_all('.clb-galeria > div > div > img', 'imgs => imgs.map(img => img.src)')

        endereco = page.text_content("div.clb-imovel-title p.endereco")

        endereco_tratado = tratar_endereco(endereco)

        preco = page.text_content("span.thumb-price[itemprop='price']").split(' ')[1]
       
        details['price'] = converter_valor(preco)

        try:
            condominio = page.text_content("span:has-text('+ Condomínio')")
            condominio_valor = condominio.split("Condomínio")[1].strip()
            details['PropertyAdministrationFee'] = converter_valor(condominio_valor)

        except Exception as e:
            print(f"Erro ao tentar pegar o valor de condomínio: {e}")

        # Tente obter o valor de "IPTU"

        try:
            iptu = page.text_content("span:has-text('+ IPTU')")
            iptu_valor = iptu.split("IPTU")[1].strip()
            details['YearlyTax'] = converter_valor(iptu_valor)
        except Exception as e:
            print(f"Erro ao tentar pegar o valor de IPTU: {e}")



        try:
            area_total = page.query_selector('#amenity-area-total span').inner_text()
            area_total = area_total.split(' ')[0]
            details['LotArea'] = area_total
        except Exception as e:
            print(f"Erro ao tentar pegar area total: {e}")

        try:
            area_privativa = page.query_selector('#amenity-area-privativa span').inner_text()
            area_privativa = area_privativa.split(' ')[0]
            details['LivingArea'] = area_privativa
        except Exception as e:
            print(f"Erro ao tentar pegar area total: {e}")

        try:
            numero_banheiros = page.locator('#amenity-banheiros span').text_content()
            details['Bathrooms'] = numero_banheiros
        except Exception as e:
            numero_banheiros = 1
            print(f"Erro ao tentar pegar area total: {e}")

        try:
            numero_quartos = page.locator('#amenity-dormitorios span').text_content()
            details['Bedrooms'] = numero_quartos
        except Exception as e:
            print(f"Erro ao tentar pegar area total: {e}")

        try:
            numero_vagas = page.locator('#amenity-dormitorios span').text_content()
            details['Garage'] = numero_vagas
        except Exception as e:
            print(f"Erro ao tentar pegar area total: {e}")
            
        try:
            p_textos = page.locator('.clb-carac-imo p').all_text_contents()
        except Exception as e:
            p_textos = []

        try:
            p_element = page.locator('#clb-descricao div.row > div:nth-child(2) > p')
            descricao = p_element.text_content()
            details['Description'] = descricao
        except Exception as e:
            try:
                # Alternativa caso o primeiro try falhe
                p_element_alt = page.locator('#clb-descricao div.row > div:nth-child(1) > p')
                descricao_alt = p_element_alt.text_content()
                details['Description'] = descricao_alt
            except Exception as e_alt:
                print(f"Erro ao tentar pegar descrição no seletor alternativo: {e_alt}")

        media = []
        for i, src in enumerate(srcs_das_imagens, start=1):
            item = {
                "medium": "image",
                "url": src,
                "primary": i == 1,  # Define como "True" apenas para o primeiro item
                "caption": f"Foto {i}"
            }
            media.append(item)

        listing = {
                "id": codigo_extraido,
                "title": titulo,
                "transaction_type": "For Sale",
                "publication_type": "STANDARD",
                "detail_view_url": link,
                "media": media,
                "video": video_url,
                "features": p_textos,
                "details": details,
                "location": {
                    "state": endereco_tratado['state'],
                    "state_name": endereco_tratado['state_name'],
                    "city": endereco_tratado['city'],
                    "neighborhood": endereco_tratado['neighborhood'],
                    "address": endereco_tratado['address'],
                    "street_number": endereco_tratado['street_number'],
                },
            }
                 

        listings.append(listing)

    browser.close()
    data = {
        "provider": "Gabriel de Souza Gomes",
        "email": "gabriel@nexusautomate.com.br",
        "contact_name": "Helder Resende",
        "telephone": "11-3450 4646",
        "listings": listings
    }

    create_listing_xml(data)

    return visited_links


def main():

    links = [
        'https://piramides.com.br/venda/residencial_comercial/florianopolis/',
    ]

    with sync_playwright() as playwright:
        for link in links:
            items = run(playwright, link)

        
    input('Aperte enter para encerrar...')


if __name__ == "__main__":

    main()