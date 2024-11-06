import os

from ramalama.common import default_image


class Quadlet:
    def __init__(self, model, args, exec_args):
        self.ai_image = model
        if hasattr(args, "MODEL"):
            self.ai_image = args.MODEL
        self.ai_image = self.ai_image.removeprefix("oci://")
        if args.name:
            self.name = args.name
        else:
            self.name = os.path.basename(self.ai_image)

        self.model = model.removeprefix("oci://")
        self.args = args
        self.exec_args = exec_args

    def generate(self):
        port_string = ""
        if hasattr(self.args, "port"):
            port_string = f"PublishPort={self.args.port}"

        name_string = ""
        if hasattr(self.args, "name") and self.args.name:
            name_string = f"ContainerName={self.args.name}"

        outfile = self.name + ".container"
        print(f"Generating quadlet file: {outfile}")
        volume = self.gen_volume()
        with open(outfile, 'w') as c:
            c.write(
                f"""\
[Unit]
Description=RamaLama {self.model} AI Model Service
After=local-fs.target

[Container]
AddDevice=-/dev/dri
AddDevice=-/dev/kfd
Exec={" ".join(self.exec_args)}
Image={default_image()}
{volume}
{name_string}
{port_string}

[Install]
# Start by default on boot
WantedBy=multi-user.target default.target
"""
            )

    def gen_volume(self):
        if os.path.exists(self.model):
            return f"Volume={self.model}:/mnt/models/model.file,ro:Z"

        outfile = self.name + ".volume"

        self.gen_image()
        print(f"Generating quadlet file: {outfile} ")
        with open(outfile, 'w') as c:
            c.write(
                f"""\
[Volume]
Driver=image
Image={self.name}.image
"""
            )
            return f"Mount=type=volume,source={self.name}.volume,dest=/mnt/models,subpath=/mounts,ro"

    def gen_image(self):
        outfile = self.name + ".image"
        print(f"Generating quadlet file: {outfile} ")
        with open(outfile, 'w') as c:
            c.write(
                f"""\
[Image]
Image={self.ai_image}
"""
            )