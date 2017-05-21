package colman66.kakuro.server;

import ratpack.handling.Handler;
import ratpack.handling.Context;
import ratpack.form.Form;
import ratpack.form.UploadedFile;

public class SolveFromImageHandler implements Handler {
  public void handle(Context context) throws Exception {
    context.parse(Form.class).then(form -> {
      UploadedFile image = form.file("image");
      if (image == null || image.getBytes().length == 0) {
        context.getResponse().status(400)
            .send("Expected a POST form with enctype=\"multipart/form-data\" and a non-empty file with the key \"image\".");
        return;
      }
      StringBuilder out = new StringBuilder();
      out.append("image is " + image.getFileName() + " " + image.getBytes().length);
      context.render(out.toString());
    });
  }
}