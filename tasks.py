from invoke import Collection

from opstrich.invoke import check, package

namespace = Collection(check, package)
