from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import time
from datetime import datetime

app = FastAPI()

async def scroll_to_bottom(page):
    previous_height = await page.evaluate('document.body.scrollHeight')
    while True:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(4)
        new_height = await page.evaluate('document.body.scrollHeight')
        pagination_visible = await page.evaluate("""
            () => {
                const pagination = document.querySelector('ul[uib-pagination]');
                return pagination && pagination.offsetParent !== null;
            }
        """)
        if new_height == previous_height or pagination_visible:
            break
        previous_height = new_height

async def scrape_page(page):
    await scroll_to_bottom(page)
    await asyncio.sleep(5)
    
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    
    produtos = []
    for item in soup.select('.componente-produto-item'):
        sku_element = item.select_one('.referencia.ng-binding')
        sku = sku_element.get_text(strip=True).replace("SKU: ", "") if sku_element else 'SKU não encontrado'
        
        descricao_element = item.select_one('.descricao.ng-binding')
        nome = descricao_element.get_text(strip=True) if descricao_element else 'Nome não encontrado'
        
        preco = item.select_one('.preco').get_text(strip=True) if item.select_one('.preco') else 'Preço não encontrado'
        peso = item.select_one('.text-muted').get_text(strip=True) if item.select_one('.text-muted') else 'Peso não encontrado'
        
        img_element = item.select_one('.imagem')
        imagem = ''
        if img_element:
            imagem = img_element['src'].split('?')[0]
        
        variacoes = [var.get_text(strip=True) for var in item.select('.variacao .descricao.ng-binding')]
        
        produto = {
            'sku': sku,
            'nome': nome,
            'preco': preco,
            'peso': peso,
            'imagem': imagem,
            'variacoes': variacoes
        }
        produtos.append(produto)
    
    return produtos

async def scrape_catalog(url):
    start_time = time.time()
    # Use default Chrome in container
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    
    await page.goto(url)
    
    await scroll_to_bottom(page)
    await asyncio.sleep(5)
    
    pagination_content = await page.content()
    pagination_soup = BeautifulSoup(pagination_content, 'html.parser')
    page_links = pagination_soup.select('ul[uib-pagination] li a.ng-binding')
    num_pages = len(page_links)
    
    all_produtos = []
    for page_num in range(1, num_pages + 1):
        if page_num > 1:
            await page.evaluate('(page_num) => document.querySelectorAll("ul[uib-pagination] li a.ng-binding")[page_num - 1].click()', page_num)
            await asyncio.sleep(5)
        
        produtos = await scrape_page(page)
        all_produtos.extend(produtos)
    
    await browser.close()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    result = f"Tempo de execução: {int(minutes)} minutos e {int(seconds)} segundos\n"
    result += f"Total de produtos encontrados: {len(all_produtos)}\n\n"
    
    for produto in all_produtos:
        result += f"SKU: {produto['sku']}\n"
        result += f"Nome: {produto['nome']}\n"
        result += f"Preço: {produto['preco']}\n"
        result += f"Peso: {produto['peso']}\n"
        result += f"Imagem: {produto['imagem']}\n"
        result += "Variações:\n"
        for var in produto['variacoes']:
            result += f" - {var}\n"
        result += "---\n"
    
    return result

@app.get("/scrape", response_class=PlainTextResponse)
async def scrape_route(url: str = Query(..., description="The catalog URL to scrape")):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    try:
        result = await scrape_catalog(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
