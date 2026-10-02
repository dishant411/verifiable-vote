"""Add local presentation assets to HTML only, never ballot data or proof APIs."""
class DemoPresentationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        if not response.streaming and response.get('Content-Type', '').startswith('text/html'):
            html = response.content.decode(response.charset)
            if '</head>' in html and '</body>' in html:
                html = html.replace('</head>', '<link rel="stylesheet" href="/demo-ui/design.css"></head>', 1)
                html = html.replace('</body>', '<script src="/demo-ui/presentation.js" defer></script></body>', 1)
                response.content = html.encode(response.charset)
                if response.has_header('Content-Length'):
                    response['Content-Length'] = str(len(response.content))
        return response
