package colman66.kakuro.server;

import ratpack.handling.Handler;
import ratpack.handling.Context;
import ratpack.form.Form;
import ratpack.form.UploadedFile;
import com.fasterxml.jackson.databind.JsonNode;
import colman66.kakuro.server.KakuroSolver;
import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import java.io.IOException;

import com.fasterxml.jackson.databind.node.ArrayNode;
import static ratpack.jackson.Jackson.json;

public class SolveFromImageHandler implements Handler {
  ObjectMapper mapper = new ObjectMapper();

  public void handle(Context context) throws Exception {
      context.parse(Form.class).then(form -> {
      UploadedFile image = form.file("image");
      if (image == null || image.getBytes().length == 0) {
        context.getResponse().status(400)
            .send("Expected a POST form with enctype=\"multipart/form-data\" and a non-empty file with the key \"image\".");
        return;
      }
      
      JsonNode board = getBoardFromImage(image);
      KakuroSolver solver = new KakuroSolver((ArrayNode) board);
      context.render(json(solver.getResultJson()));
    });
  }

  private JsonNode getBoardFromImage(UploadedFile image) throws JsonProcessingException, IOException
  {
    // TODO: call python code
    String dummyBoardJson =
      "[[\"X\", {\"down\":3}, {\"down\":4}, \"X\", \"X\", \"X\", \"X\", {\"down\":15}, {\"down\":3}]," +
      "[{\"right\":4}, null, null, {\"down\":16}, {\"down\":6}, \"X\", {\"right\":3}, null, null]," +
      "[{\"right\":10}, null, null, null, null, {\"down\":14}, {\"down\":16, \"right\":7}, null, null]," +
      "[\"X\", \"X\", {\"down\":21, \"right\":16}, null, null, null, null, null, \"X\"]," +
      "[\"X\", {\"right\":3}, null, null, {\"down\":3, \"right\":11}, null, null, null, \"X\"]," +
      "[\"X\",{\"right\":6}, null, null, null, {\"down\":4, \"right\":10}, null, null, \"X\"]," +
      "[\"X\", {\"down\":4, \"right\":19}, null, null, null, null, null, {\"down\":3}, {\"down\":4}]," +
      "[{\"right\":6}, null, null, \"X\", {\"right\":10}, null, null, null, null]," +
      "[{\"right\":7}, null, null, \"X\", \"X\", \"X\", {\"right\":4}, null, null]]";

    return mapper.readTree(dummyBoardJson);
  }
}