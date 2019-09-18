from app.domain.model.documento import Documento
from app.domain.model.pagina import Pagina
from app.domain.model.repository.documento import DocumentoRepository
from app.domain.model.repository.pagina import PaginaRepository
from app.logger import log_performance

import attr

from glom import glom


@attr.s(slots=True, frozen=True)
class EventHandler:

    _app = attr.ib()
    documentoRepository = attr.ib(default=DocumentoRepository())
    paginaRepository = attr.ib(default=PaginaRepository())

    @log_performance()
    async def process(self, payload):
        documento_id = await self._process_documento(payload)
        await self._process_paginas(payload, documento_id)

    async def _process_documento(self, payload):
        documento = Documento(
            numero=glom(payload, 'documento'),
            descricao=glom(payload, 'descricao')
        )
        self.documentoRepository.salvar(documento)
        documento_id = self.documentoRepository.recuperar(documento)
        return documento_id

    async def _process_paginas(self, payload, documento_id):
        paginas = glom(payload, 'paginas')
        # paginas_operations = list()
        # for pagina in paginas:
        #     paginas_operations.append(Pagina(
        #         numero=pagina.get('numero'),
        #         corpo=pagina.get('corpo'),
        #         documento_id=documento_id
        #     ))
        # self.paginaRepository.recuperar(paginas_operations)
        for pagina in paginas:
            self.paginaRepository.recuperar(Pagina(
                numero=pagina.get('numero'),
                corpo=pagina.get('corpo'),
                documento_id=documento_id
            ))
