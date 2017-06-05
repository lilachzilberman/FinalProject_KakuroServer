package colman66.kakuro.server;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import javax.servlet.http.HttpServletRequest;
import org.apache.commons.fileupload.*;
import org.apache.commons.fileupload.disk.*;
import org.apache.commons.fileupload.servlet.*;
import org.apache.commons.io.*;
import spark.*;

public class SolveFromImageHandler implements Route {
  final ObjectMapper mapper = new ObjectMapper();

  ServletFileUpload uploadParser;

  public SolveFromImageHandler() throws IOException {
    DiskFileItemFactory factory = new DiskFileItemFactory();
    File uploadDir = Files.createTempDirectory(null).toFile();
    Runtime.getRuntime().addShutdownHook(new Thread() {
      public void run() {
        try {
          FileUtils.deleteDirectory(uploadDir);
        } catch (IOException e) {
        }
      }
    });
    factory.setRepository(uploadDir);
    uploadParser = new ServletFileUpload(factory);
  }

  public Object handle(Request request, Response response) throws Exception {
    boolean useInternalFormat = "internal".equals(request.queryParams("format"));
    HttpServletRequest raw = request.raw();
    List<FileItem> items = uploadParser.parseRequest(raw);

    FileItem image = items.stream().filter(p -> p.getFieldName().equals("image")).findAny().orElse(null);

    if (image == null || image.getSize() == 0) {
      response.status(400);
      return "Expected a POST form with enctype=\"multipart/form-data\" and a non-empty file with the key \"image\".";
    }

    JsonNode board = getBoardFromImage(image);
    KakuroSolver solver = new KakuroSolver((ArrayNode) board);
    response.type("application/json");

    if (useInternalFormat)
    {
          return mapper.writeValueAsString(solver.getResultJson());
    }

    return mapper.writeValueAsString(BoardConversions.appFromInternal(solver.getResultJson()));
  }

  private JsonNode getBoardFromImage(FileItem image) throws JsonProcessingException, IOException {
    // TODO: call python code
    String dummyBoardJson = "[[\"X\", {\"down\":3}, {\"down\":4}, \"X\", \"X\", \"X\", \"X\", {\"down\":15}, {\"down\":3}],"
        + "[{\"right\":4}, null, null, {\"down\":16}, {\"down\":6}, \"X\", {\"right\":3}, null, null],"
        + "[{\"right\":10}, null, null, null, null, {\"down\":14}, {\"down\":16, \"right\":7}, null, null],"
        + "[\"X\", \"X\", {\"down\":21, \"right\":16}, null, null, null, null, null, \"X\"],"
        + "[\"X\", {\"right\":3}, null, null, {\"down\":3, \"right\":11}, null, null, null, \"X\"],"
        + "[\"X\",{\"right\":6}, null, null, null, {\"down\":4, \"right\":10}, null, null, \"X\"],"
        + "[\"X\", {\"down\":4, \"right\":19}, null, null, null, null, null, {\"down\":3}, {\"down\":4}],"
        + "[{\"right\":6}, null, null, \"X\", {\"right\":10}, null, null, null, null],"
        + "[{\"right\":7}, null, null, \"X\", \"X\", \"X\", {\"right\":4}, null, null]]";

    JsonNode pyjson = mapper.readTree(dummyBoardJson);
    return pyjson;
  }
}