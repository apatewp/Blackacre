import logging
import blackacre.bootstrap as bootstrap

from blackacre_pb2 import BlackacreSentenceSegmenterResponse, BlackacreHealthCheckResponse
from blackacre_pb2_grpc import BlackacreServicer, add_BlackacreServicer_to_server
from blackacre.pipeline import SentencePipeline

from blackacre.utils import dehyphenate,basic_string_cleaner

class BlackacreServer(BlackacreServicer):
    def __init__(self, rules=[]):
        self.sentence_segmenter = SentencePipeline()

    def HealthCheck(self, request, context):
        resp = BlackacreHealthCheckResponse(status="OK")
        return resp

    def GetSentences(self, request, context):
        fns = [dehyphenate, basic_string_cleaner]
        request = request.text
        for fn in fns:
            request = fn(request)
        sentences = self.sentence_segmenter.get_sentences(request)
        resp = BlackacreSentenceSegmenterResponse(sentences=[sent.text for sent in sentences])
        return resp


if __name__ == '__main__':
    bootstrap.logger()
    args = bootstrap.arg_parser()
    rules = bootstrap.rules(args)
    server = bootstrap.server(args)

    bootstrap.servicer(server, BlackacreServer, {"rules": rules})

    server.start()

    logging.info('server ready on port %r', args.port)

    server.wait_for_termination()
