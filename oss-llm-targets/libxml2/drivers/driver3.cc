#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "libxml/xmlschemastypes.h"
#include "libxml/parser.h"
#include "libxml/xpath.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  xmlDocPtr doc = xmlReadMemory(reinterpret_cast<const char*>(data), size,
                                nullptr, nullptr, 0);
  if (doc == nullptr) {
    return 0;
  }

  xmlXPathContextPtr xpath_context = xmlXPathNewContext(doc);
  if (xpath_context == nullptr) {
    xmlFreeDoc(doc);
    return 0;
  }

  xmlXPathObjectPtr xpath_object = xmlXPathEvalExpression(
      BAD_CAST "//", xpath_context);
  if (xpath_object == nullptr) {
    xmlXPathFreeContext(xpath_context);
    xmlFreeDoc(doc);
    return 0;
  }

  xmlNodeSetPtr node_set = xpath_object->nodesetval;
  if (node_set == nullptr) {
    xmlXPathFreeObject(xpath_object);
    xmlXPathFreeContext(xpath_context);
    xmlFreeDoc(doc);
    return 0;
  }

  xmlXPathCompExprPtr comp = xmlXPathCompile(BAD_CAST "count(//)");
  if (comp == nullptr) {
    xmlXPathFreeObject(xpath_object);
    xmlXPathFreeContext(xpath_context);
    xmlFreeDoc(doc);
    return 0;
  }

  xmlSchemaValidCtxtPtr valid_ctxt = xmlSchemaNewValidCtxt(nullptr);
  if (valid_ctxt == nullptr) {
    xmlXPathFreeCompExpr(comp);
    xmlXPathFreeObject(xpath_object);
    xmlXPathFreeContext(xpath_context);
    xmlFreeDoc(doc);
    return 0;
  }

  int options = 0;
  xmlSchemaValidateFile(valid_ctxt, nullptr, options);

  xmlSchemaFreeValidCtxt(valid_ctxt);
  xmlXPathFreeCompExpr(comp);
  xmlXPathFreeObject(xpath_object);
  xmlXPathFreeContext(xpath_context);
  xmlFreeDoc(doc);

  return 0;
}

