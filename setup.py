from setuptools import Extension, find_packages, setup
import os
import shutil


dir_path = os.path.dirname(os.path.abspath(__file__))
pkg_dir = os.path.join(dir_path, "src", "systemd_dbus")
priv_prefix = os.environ.get("SDBUS_PREFIX", "/opt/sdbus-priv")
priv_soname = "libsystemd-priv.so.0"

should_vendor = bool(os.environ.get("SDBUS_VENDOR"))

if should_vendor:
    include = os.path.join(priv_prefix, "include")
    lib = os.path.join(priv_prefix, "lib")
    src_so = os.path.join(lib, priv_soname)
    shutil.copy(src_so, os.path.join(pkg_dir, priv_soname))

    ext_args = {
        "include_dirs": [include],
        "library_dirs": [lib],
        "libraries": ["systemd-priv"],
        "extra_link_args": ["-Wl,-rpath,$ORIGIN", "-Wl,-z,origin"]
    }
else:
    ext_args = {
        "libraries": ["systemd"],
    }

native = Extension(
    name="systemd_dbus._sdbus",
    sources=["src/systemd_dbus/c/systemd_dbus.c", "src/systemd_dbus/c/dbus_api.c"],
    extra_compile_args=["-fPIC", "-Wall", "-Wextra", "-std=gnu99", "-Wundef"],
    **ext_args,
)


setup(
    name="systemd-dbus",
    version="0.4",
    description="Thin Python bindings for a minimal set of systemd service management commands, using sd-bus",
    author="Jeffrey Smith",
    author_email="jeffrey.smith@acceldata.io",
    license="Apache-2.0",
    python_requires=">=2.7",
    package_data={"systemd_dbus": [priv_soname]} if should_vendor else {},
    install_requires=["jinja2 == 2.11.3; python_version == '2.7'"],
    ext_modules=[native],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False,
)
