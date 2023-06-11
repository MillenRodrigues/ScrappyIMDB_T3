import scrapy
import csv


class MovieSpider(scrapy.Spider):
    name = "movie"
    # lista dos 250 filmes mais populares
    start_urls = ["https://www.imdb.com/chart/top/?ref_=nv_mv_250"]

    # função que trata a página inicial com todos os links para os filmes
    def parse(self, response):
        # link do titulo abaixo dos posters dos filmes
        seletor_do_link="td.titleColumn a"
        links = response.css(seletor_do_link)
        qtd = len(links)
        print(f'{qtd} links encontrados, iniciando navegação nos links')
        
        # cria o csv em branco
        with open('./dados/csv/filmes.csv', 'w', newline='', encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, delimiter=';', fieldnames=['titulo','ano','classificacao','duracao','sinopse','direcao','roteiristas','artistas','nota'])
            dict_writer.writeheader() 


        # salva a pagina HTML para entrega junto com o trabalho
        with open(f'./dados/html/filmes.html', 'wb') as html_file:
            html_file.write(response.body)

        for link in links:
            url = "https://www.imdb.com" + link.css('::attr(href)').get()
            txt = link.css('::text').get()
            print(f"Coletando dados de {txt}")
            yield scrapy.Request(url, callback=self.parse_text)
    
    # função que interpreta cada página e gera o CSv do filme
    def parse_text(self, response):
        titulo = response.css("h1 span::text").get().replace(":","") # ":" no nome quebra a geração de arquivos
        linha_ano = response.css("ul.ipc-inline-list.ipc-inline-list--show-dividers")[1]
        ano = linha_ano.css("li")[0].css('::text').get()
        classificacao = linha_ano.css("li")[1].css('::text').get()
        duracao = linha_ano.css("li")[2].css('::text').get()
        sinopse = response.css('[data-testid="plot-xl"]::text').get()
        direcao = response.css('[data-testid="title-pc-principal-credit"]')[0].css('.ipc-metadata-list-item__content-container ::text').getall()
        roteiristas = response.css('[data-testid="title-pc-principal-credit"]')[1].css('.ipc-metadata-list-item__content-container ::text').getall()
        artistas = response.css('[data-testid="title-pc-principal-credit"]')[2].css('.ipc-metadata-list-item__content-container ::text').getall()
        nota = response.css('[data-testid="hero-rating-bar__aggregate-rating__score"] ::text')[0].get()

        movie = {
            'titulo': titulo,
            'ano': ano,
            'classificacao': classificacao,
            'duracao': duracao,
            'sinopse': sinopse,
            'direcao': ', '.join(eval(str(direcao))),
            'roteiristas': ', '.join(eval(str(roteiristas))),
            'artistas': ', '.join(eval(str(artistas))),
            'nota': nota
        }

        print(movie)

        # salva a pagina HTML para entrega junto com o trabalho
        with open(f'./dados/html/filmes/{titulo}.html', 'wb') as html_file:
            html_file.write(response.body)
        
        # adiciona a página no CSV
        with open('./dados/csv/filmes.csv', 'a', newline='', encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, delimiter=';', fieldnames=movie.keys())
            dict_writer.writerow(movie)
        
        print(f"Parse de {titulo} finalizado")

    