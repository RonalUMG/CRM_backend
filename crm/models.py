from clients.models import Client as ClientBase
from clients.models import Note as NoteBase


class Client(ClientBase):
    class Meta:
        proxy = True
        app_label = "crm"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Note(NoteBase):
    class Meta:
        proxy = True
        app_label = "crm"
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
