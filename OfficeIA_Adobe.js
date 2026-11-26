app.addMenuItem({
    cName: "OfficeIA_AnalisarPDF",
    cUser: "⚡ Gerar Relatório com OfficeIA",
    cParent: "Edit",
    cExec: "executarOfficeIA()",
    cEnable: "event.rc = (event.target != null);"
});

function executarOfficeIA() {
    var numPaginas = this.numPages;
    var textoCompleto = "";

    for (var p = 0; p < numPaginas; p++) {
        var numPalavras = this.getPageNumWords(p);
        for (var w = 0; w < numPalavras; w++) {
            textoCompleto += this.getPageNthWord(p, w, false) + " ";
        }
    }

    var resp = app.response({
        cQuestion: "O que você deseja analisar neste PDF?",
        cTitle: "OfficeIA - Assistente PDF"
    });

    if (resp != null) {
        Net.HTTP.request({
            cVerb: "POST",
            cURL: "https://onrender.com/api/analisar-dados-diretos",
            oRequest: {
                dados: [{ Categoria: "Texto PDF", Valor: numPaginas }],
                comando: resp + " | Conteúdo: " + textoCompleto.substring(0, 2000)
            },
            oHandler: {
                response: function(msg, uri, err) {
                    app.alert("Relatório processado com sucesso pela OfficeIA!");
                }
            }
        });
    }
}
